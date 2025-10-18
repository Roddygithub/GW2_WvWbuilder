"""
Configuration du cache de second niveau SQLAlchemy avec Redis.
"""

from typing import Any, Callable, Iterator, TypeVar

from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session as SessionType
from sqlalchemy import event
from sqlalchemy.orm import Mapper

from app.core.config import settings
from app.core.logging_config import logger

# Type variable for the model
ModelType = TypeVar("ModelType", bound=Any)


def configure_sqlalchemy_caching() -> None:
    """
    Configure le cache de second niveau SQLAlchemy avec Dogpile.

    Cette fonction doit être appelée au démarrage de l'application.
    """
    if not settings.CACHE_ENABLED:
        logger.info("SQLAlchemy second level cache is disabled")
        return

    try:
        from dogpile.cache.region import make_region
        from sqlalchemy_redis import RedisSession
        from sqlalchemy_redis.py3k import RedisCacheImpl
        from sqlalchemy_redis.cache import RedisCache

        # Configuration des régions de cache
        regions = {}

        for region_name, region_config in settings.CACHE_REGIONS.items():
            region = make_region(
                name=region_name,
                function_key_generator=lambda *args, **kw: "{0}:{1}".format(
                    kw.get("fn", "").__name__, ":".join(str(arg) for arg in args[1:])
                ),
            ).configure(
                settings.CACHE_IMPLEMENTATION,
                expiration_time=region_config["expiration_time"],
                arguments=(
                    {
                        "host": settings.REDIS_HOST,
                        "port": settings.REDIS_PORT,
                        "db": settings.REDIS_DB,
                        "password": settings.REDIS_PASSWORD,
                        "socket_timeout": 5,
                        "socket_connect_timeout": 5,
                        "retry_on_timeout": True,
                        "encoding": "utf-8",
                    }
                    if settings.CACHE_IMPLEMENTATION == "redis"
                    else {}
                ),
            )
            regions[region_name] = region

        # Configuration du cache de requêtes SQLAlchemy
        from sqlalchemy.orm import configure_mappers
        from sqlalchemy.orm.session import _sessions
        from sqlalchemy.orm.query import Query as _Query

        # Configuration du cache de requêtes
        class CachingQuery(_Query):
            """
            Query personnalisé qui prend en charge le cache de second niveau.
            """

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.cache_region = regions["default"]
                self.cache_key = None
                self.cache_invalidate = False
                super().__init__(*args, **kwargs)

            def get(self, ident: Any, **kwargs: Any) -> Any:
                """
                Récupère un objet par sa clé primaire avec mise en cache.
                """
                if not self._criterion:
                    # Pas de critère de requête, on peut utiliser le cache
                    cache_key = f"{self._entities[0].entity._cache_namespace}:{ident}"
                    cached = self.cache_region.get(cache_key)
                    if cached is not None:
                        return cached

                # Si pas en cache ou si la requête a des critères supplémentaires
                result = super().get(ident, **kwargs)

                if result is not None and not self._criterion:
                    # Mise en cache du résultat
                    self.cache_region.set(cache_key, result)

                return result

            def __iter__(self) -> Iterator[Any]:
                """
                Exécute la requête et met en cache le résultat si nécessaire.
                """
                if self.cache_key and not self.cache_invalidate:
                    # Essayer de récupérer depuis le cache
                    cached = self.cache_region.get(self.cache_key)
                    if cached is not None:
                        return iter(cached)

                # Exécuter la requête
                result = list(super().__iter__())

                # Mettre en cache le résultat si nécessaire
                if self.cache_key and not self.cache_invalidate:
                    self.cache_region.set(self.cache_key, result)

                return iter(result)

            def cache(self, key: str, region: str = "default") -> "CachingQuery":
                """
                Active la mise en cache pour cette requête.

                Args:
                    key: Clé de cache
                    region: Nom de la région de cache à utiliser

                Returns:
                    La requête avec la configuration de cache
                """
                self.cache_key = key
                if region in regions:
                    self.cache_region = regions[region]
                return self

            def invalidate_cache(self) -> "CachingQuery":
                """
                Invalide le cache pour cette requête.

                Returns:
                    La requête avec le cache invalidé
                """
                self.cache_invalidate = True
                return self

        # Configuration des écouteurs d'événements pour l'invalidation du cache
        @event.listens_for(Session, "after_flush")
        def receive_after_flush(session: SessionType, context: Any) -> None:
            """
            Invalide le cache après un flush de session.
            """
            if not settings.CACHE_ENABLED:
                return

            for instance in session.dirty.union(session.deleted):
                if hasattr(instance, "_cache_namespace"):
                    # Invalider le cache pour cet objet
                    cache_key = f"{instance._cache_namespace}:{instance.id}"
                    regions["default"].delete(cache_key)

        # Configuration du cache pour les relations
        @event.listens_for(Mapper, "after_configured")
        def setup_cache_listeners() -> None:
            """
            Configure les écouteurs d'événements pour le cache des relations.
            """
            from sqlalchemy.orm import mapper

            for mapper in mapper._mapper_registry:
                if hasattr(mapper.class_, "_cache_namespace"):
                    # Configurer l'invalidation du cache pour les relations
                    for prop in mapper.iterate_properties:
                        if hasattr(prop, "mapper"):

                            @event.listens_for(mapper.class_, "refresh")
                            def receive_refresh(
                                target: Any, context: Any, attrs: Any
                            ) -> None:
                                if hasattr(target, "_cache_namespace"):
                                    cache_key = f"{target._cache_namespace}:{target.id}"
                                    regions["default"].delete(cache_key)

        # Configuration de la session pour utiliser notre Query personnalisée
        Session.configure(query_cls=CachingQuery)

        logger.info("SQLAlchemy second level cache configured")

    except ImportError as e:
        logger.warning(f"Failed to configure SQLAlchemy second level cache: {e}")
        logger.warning(
            "Falling back to no caching. Install 'sqlalchemy-redis' and 'dogpile.cache' to enable caching."
        )


def cache_region(
    region_name: str = "default",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Décorateur pour mettre en cache le résultat d'une fonction.

    Args:
        region_name: Nom de la région de cache à utiliser

    Returns:
        Le décorateur de fonction
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not settings.CACHE_ENABLED:
            return func

        from dogpile.cache.region import make_region

        region = make_region().configure(
            settings.CACHE_IMPLEMENTATION,
            expiration_time=settings.CACHE_REGIONS.get(region_name, {}).get(
                "expiration_time", 300
            ),
            arguments=(
                {
                    "host": settings.REDIS_HOST,
                    "port": settings.REDIS_PORT,
                    "db": settings.REDIS_DB,
                    "password": settings.REDIS_PASSWORD,
                }
                if settings.CACHE_IMPLEMENTATION == "redis"
                else {}
            ),
        )

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Générer une clé de cache unique basée sur les arguments
            cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"

            # Essayer de récupérer depuis le cache
            cached = region.get(cache_key)
            if cached is not None:
                return cached

            # Sinon, exécuter la fonction et mettre en cache le résultat
            result = func(*args, **kwargs)
            region.set(cache_key, result)
            return result

        return wrapper

    return decorator
