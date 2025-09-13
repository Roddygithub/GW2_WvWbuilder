"""
Tests unitaires pour les modèles de base de l'application.
"""
import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.models.base import BaseModel, BaseUUIDModel, BaseTimeStampedModel, BaseUUIDTimeStampedModel
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

# Création d'un modèle de test basé sur les classes de base
TestBase = declarative_base()

class TestModel(BaseModel, TestBase):
    """Modèle de test pour BaseModel."""
    __tablename__ = "test_model"
    name = Column(String(100), nullable=False)
    value = Column(Integer, default=0)

class TestUUIDModel(BaseUUIDModel, TestBase):
    """Modèle de test pour BaseUUIDModel."""
    __tablename__ = "test_uuid_model"
    name = Column(String(100), nullable=False)

class TestTimeStampedModel(BaseTimeStampedModel, TestBase):
    """Modèle de test pour BaseTimeStampedModel."""
    __tablename__ = "test_timestamped_model"
    name = Column(String(100), nullable=False)

class TestUUIDTimeStampedModel(BaseUUIDTimeStampedModel, TestBase):
    """Modèle de test pour BaseUUIDTimeStampedModel."""
    __tablename__ = "test_uuid_timestamped_model"
    name = Column(String(100), nullable=False)

@pytest.mark.unit
class TestBaseModel:
    """Tests pour le modèle de base BaseModel."""
    
    def test_base_model_creation(self):
        """Teste la création d'une instance de BaseModel."""
        model = TestModel(name="Test", value=42)
        
        # Vérifier que l'ID est généré
        assert hasattr(model, 'id')
        assert model.id is not None
        
        # Vérifier que les attributs sont correctement définis
        assert model.name == "Test"
        assert model.value == 42
        
        # Vérifier que l'objet est ajouté à la session (sans la sauvegarder)
        assert model in model._sa_instance_state.session
    
    def test_base_model_repr(self):
        """Teste la représentation en chaîne du modèle."""
        model = TestModel(name="Test", value=42)
        model.id = 1  # Définir un ID fixe pour le test
        
        # Vérifier que la représentation contient le nom de la classe et l'ID
        assert "TestModel" in repr(model)
        assert "1" in repr(model)
        assert "name='Test'" in repr(model)
    
    def test_base_model_to_dict(self):
        """Teste la conversion du modèle en dictionnaire."""
        model = TestModel(name="Test", value=42)
        model.id = 1  # Définir un ID fixe pour le test
        
        # Convertir en dictionnaire
        result = model.to_dict()
        
        # Vérifier que toutes les colonnes sont incluses
        assert result["id"] == 1
        assert result["name"] == "Test"
        assert result["value"] == 42
        
        # Vérifier que les méthodes et attributs privés ne sont pas inclus
        assert "_sa_instance_state" not in result
        assert "metadata" not in result
    
    def test_base_model_to_dict_exclude(self):
        """Teste l'exclusion de champs lors de la conversion en dictionnaire."""
        model = TestModel(name="Test", value=42)
        model.id = 1
        
        # Exclure le champ 'value'
        result = model.to_dict(exclude={"value"})
        
        # Vérifier que 'value' est exclu
        assert "id" in result
        assert "name" in result
        assert "value" not in result

@pytest.mark.unit
class TestBaseUUIDModel:
    """Tests pour le modèle BaseUUIDModel."""
    
    def test_uuid_model_creation(self):
        """Teste la création d'une instance de BaseUUIDModel."""
        model = TestUUIDModel(name="Test UUID")
        
        # Vérifier que l'ID est un UUID valide
        assert hasattr(model, 'id')
        assert isinstance(model.id, UUID)
        
        # Vérifier que l'attribut est correctement défini
        assert model.name == "Test UUID"
    
    def test_uuid_model_with_custom_id(self):
        """Teste la création avec un UUID personnalisé."""
        custom_uuid = uuid4()
        model = TestUUIDModel(id=custom_uuid, name="Custom UUID")
        
        # Vérifier que l'ID personnalisé est utilisé
        assert model.id == custom_uuid
    
    def test_uuid_model_repr(self):
        """Teste la représentation en chaîne du modèle UUID."""
        custom_uuid = uuid4()
        model = TestUUIDModel(id=custom_uuid, name="Test UUID")
        
        # Vérifier que la représentation contient l'UUID
        assert "TestUUIDModel" in repr(model)
        assert str(custom_uuid) in repr(model)
        assert "name='Test UUID'" in repr(model)

@pytest.mark.unit
class TestBaseTimeStampedModel:
    """Tests pour le modèle BaseTimeStampedModel."""
    
    def test_timestamped_model_creation(self):
        """Teste la création d'une instance de BaseTimeStampedModel."""
        model = TestTimeStampedModel(name="Test Timestamped")
        
        # Vérifier que les horodatages sont définis
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        
        # Vérifier que les horodatages sont des objets datetime
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        
        # Vérifier que created_at et updated_at sont initialisés à la même valeur
        assert model.created_at == model.updated_at
        
        # Vérifier que les horodatages sont en UTC
        assert model.created_at.tzinfo == timezone.utc
        assert model.updated_at.tzinfo == timezone.utc
    
    def test_timestamped_model_update(self):
        """Teste la mise à jour des horodatages."""
        model = TestTimeStampedModel(name="Test Timestamped")
        original_created = model.created_at
        original_updated = model.updated_at
        
        # Simuler une mise à jour
        model.name = "Updated Name"
        
        # Vérifier que created_at n'a pas changé
        assert model.created_at == original_created
        
        # Vérifier que updated_at a été mis à jour (dans la réalité, cela se ferait via un événement SQLAlchemy)
        # Pour les besoins du test, nous vérifions simplement que la méthode existe
        assert hasattr(model, 'update_timestamp')
        
        # Appeler manuellement update_timestamp pour tester
        model.update_timestamp()
        assert model.updated_at > original_updated
    
    def test_timestamped_model_to_dict(self):
        """Teste la conversion en dictionnaire avec les horodatages."""
        model = TestTimeStampedModel(name="Test Timestamped")
        model.id = 1
        
        # Convertir en dictionnaire
        result = model.to_dict()
        
        # Vérifier que les horodatages sont inclus
        assert "created_at" in result
        assert "updated_at" in result
        
        # Vérifier le format des horodatages (devrait être une chaîne ISO)
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)

@pytest.mark.unit
class TestBaseUUIDTimeStampedModel:
    """Tests pour le modèle BaseUUIDTimeStampedModel."""
    
    def test_uuid_timestamped_model_creation(self):
        """Teste la création d'une instance de BaseUUIDTimeStampedModel."""
        model = TestUUIDTimeStampedModel(name="Test UUID Timestamped")
        
        # Vérifier que l'ID est un UUID valide
        assert hasattr(model, 'id')
        assert isinstance(model.id, UUID)
        
        # Vérifier que les horodatages sont définis
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        
        # Vérifier que les horodatages sont des objets datetime
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
    
    def test_uuid_timestamped_model_to_dict(self):
        """Teste la conversion en dictionnaire avec UUID et horodatages."""
        custom_uuid = uuid4()
        model = TestUUIDTimeStampedModel(id=custom_uuid, name="Test UUID Timestamped")
        
        # Convertir en dictionnaire
        result = model.to_dict()
        
        # Vérifier que l'UUID est correctement sérialisé
        assert result["id"] == str(custom_uuid)
        
        # Vérifier que les horodatages sont inclus
        assert "created_at" in result
        assert "updated_at" in result
        
        # Vérifier que le nom est correct
        assert result["name"] == "Test UUID Timestamped"
    
    def test_uuid_timestamped_model_with_custom_timestamps(self):
        """Teste la création avec des horodatages personnalisés."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        model = TestUUIDTimeStampedModel(
            name="Custom Timestamps",
            created_at=custom_time,
            updated_at=custom_time
        )
        
        # Vérifier que les horodatages personnalisés sont utilisés
        assert model.created_at == custom_time
        assert model.updated_at == custom_time
        
        # Vérifier la sérialisation en dictionnaire
        result = model.to_dict()
        assert result["created_at"] == custom_time.isoformat()
        assert result["updated_at"] == custom_time.isoformat()

# Tests pour les méthodes utilitaires des modèles

@pytest.mark.unit
class TestModelUtilities:
    """Tests pour les méthodes utilitaires des modèles."""
    
    def test_model_equality(self):
        """Teste l'égalité des modèles basée sur l'ID."""
        # Créer deux modèles avec le même ID
        model1 = TestModel(id=1, name="Test 1")
        model2 = TestModel(id=1, name="Test 2")
        
        # Créer un modèle avec un ID différent
        model3 = TestModel(id=2, name="Test 3")
        
        # Vérifier l'égalité
        assert model1 == model2
        assert model1 != model3
        
        # Vérifier l'inégalité avec d'autres types
        assert model1 != "not a model"
    
    def test_model_hash(self):
        """Teste le hachage des modèles basé sur l'ID."""
        # Créer deux modèles avec le même ID
        model1 = TestModel(id=1, name="Test 1")
        model2 = TestModel(id=1, name="Test 2")
        
        # Créer un modèle avec un ID différent
        model3 = TestModel(id=2, name="Test 3")
        
        # Vérifier que les hachages sont égaux pour les modèles avec le même ID
        assert hash(model1) == hash(model2)
        
        # Vérifier que les hachages sont différents pour les modèles avec des IDs différents
        assert hash(model1) != hash(model3)
    
    def test_model_copy(self):
        """Teste la copie d'un modèle."""
        # Créer un modèle avec des valeurs par défaut
        original = TestModel(name="Original", value=42)
        original.id = 1
        original_created = datetime(2023, 1, 1, tzinfo=timezone.utc)
        original.created_at = original_created
        original.updated_at = original_created
        
        # Faire une copie
        copy = original.copy()
        
        # Vérifier que l'ID n'est pas copié (généralement, on veut un nouvel ID)
        assert copy.id is None
        
        # Vérifier que les autres attributs sont copiés
        assert copy.name == "Original"
        assert copy.value == 42
        
        # Vérifier que les horodatages ne sont pas copiés (doivent être régénérés)
        assert copy.created_at != original_created
        assert copy.updated_at != original_created
        
        # Vérifier que les horodatages sont définis
        assert copy.created_at is not None
        assert copy.updated_at is not None
