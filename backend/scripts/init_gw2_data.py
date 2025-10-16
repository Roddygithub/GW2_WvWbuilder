"""
Script d'initialisation des données Guild Wars 2
Charge les professions et elite specializations depuis l'API GW2 officielle
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.profession import Profession
from app.models.elite_specialization import EliteSpecialization

# Configuration
GW2_API_BASE = "https://api.guildwars2.com/v2"
DB_PATH = Path(__file__).parent.parent / "gw2_wvwbuilder.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"🔧 Initialisation données GW2")
print(f"📁 Base de données: {DB_PATH}")
print(f"🌐 API GW2: {GW2_API_BASE}")
print()

# Créer engine et session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


async def fetch_gw2_professions():
    """Récupère toutes les professions depuis l'API GW2."""
    print("📥 Récupération professions GW2...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Liste des IDs
        response = await client.get(f"{GW2_API_BASE}/professions")
        profession_ids = response.json()
        print(f"   Trouvé {len(profession_ids)} professions")
        
        # Détails de chaque profession
        professions = []
        for prof_id in profession_ids:
            try:
                response = await client.get(f"{GW2_API_BASE}/professions/{prof_id}")
                prof_data = response.json()
                professions.append(prof_data)
                print(f"   ✓ {prof_data['name']}")
            except Exception as e:
                print(f"   ✗ Erreur {prof_id}: {e}")
        
        return professions


async def fetch_gw2_specializations():
    """Récupère toutes les specializations depuis l'API GW2."""
    print("\n📥 Récupération specializations GW2...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Liste des IDs
        response = await client.get(f"{GW2_API_BASE}/specializations")
        spec_ids = response.json()
        print(f"   Trouvé {len(spec_ids)} specializations")
        
        # Détails de chaque specialization
        specializations = []
        elite_count = 0
        for spec_id in spec_ids:
            try:
                response = await client.get(f"{GW2_API_BASE}/specializations/{spec_id}")
                spec_data = response.json()
                
                # Filtrer seulement les elites
                if spec_data.get('elite'):
                    specializations.append(spec_data)
                    elite_count += 1
                    print(f"   ✓ {spec_data['name']} ({spec_data['profession']}) [Elite]")
            except Exception as e:
                print(f"   ✗ Erreur {spec_id}: {e}")
        
        print(f"   Total elite specs: {elite_count}")
        return specializations


def save_professions(professions_data):
    """Sauvegarde les professions en base de données."""
    print("\n💾 Sauvegarde professions en DB...")
    
    session = Session()
    saved_count = 0
    updated_count = 0
    
    for prof_data in professions_data:
        try:
            # Chercher si existe déjà
            existing = session.query(Profession).filter(
                Profession.name == prof_data['name']
            ).first()
            
            if existing:
                # Mettre à jour
                existing.icon_url = prof_data.get('icon_big', prof_data.get('icon', ''))
                existing.is_active = True
                existing.game_modes = ['wvw', 'pvp', 'pve']
                updated_count += 1
                print(f"   ↻ {prof_data['name']} (mis à jour)")
            else:
                # Créer nouveau
                profession = Profession(
                    name=prof_data['name'],
                    icon_url=prof_data.get('icon_big', prof_data.get('icon', '')),
                    description=f"{prof_data['name']} - {prof_data.get('armor', 'Unknown')} armor",
                    is_active=True,
                    game_modes=['wvw', 'pvp', 'pve']
                )
                session.add(profession)
                saved_count += 1
                print(f"   ✓ {prof_data['name']} (créé)")
            
        except Exception as e:
            print(f"   ✗ Erreur {prof_data['name']}: {e}")
    
    session.commit()
    print(f"\n   📊 Créés: {saved_count} | Mis à jour: {updated_count}")
    session.close()
    return saved_count + updated_count


def save_elite_specializations(specs_data, professions_map):
    """Sauvegarde les elite specializations en base de données."""
    print("\n💾 Sauvegarde elite specializations en DB...")
    
    session = Session()
    saved_count = 0
    updated_count = 0
    
    for spec_data in specs_data:
        try:
            # Trouver profession_id
            profession_name = spec_data['profession']
            profession = professions_map.get(profession_name)
            
            if not profession:
                print(f"   ⚠️  Profession {profession_name} non trouvée pour {spec_data['name']}")
                continue
            
            # Chercher si existe déjà
            existing = session.query(EliteSpecialization).filter(
                EliteSpecialization.name == spec_data['name']
            ).first()
            
            if existing:
                # Mettre à jour
                existing.icon_url = spec_data.get('icon', '')
                existing.profession_id = profession.id
                updated_count += 1
                print(f"   ↻ {spec_data['name']} ({profession_name}) (mis à jour)")
            else:
                # Créer nouveau
                elite_spec = EliteSpecialization(
                    name=spec_data['name'],
                    icon_url=spec_data.get('icon', ''),
                    description=f"{spec_data['name']} elite specialization for {profession_name}",
                    profession_id=profession.id
                )
                session.add(elite_spec)
                saved_count += 1
                print(f"   ✓ {spec_data['name']} ({profession_name}) (créé)")
            
        except Exception as e:
            print(f"   ✗ Erreur {spec_data['name']}: {e}")
    
    session.commit()
    print(f"\n   📊 Créés: {saved_count} | Mis à jour: {updated_count}")
    session.close()
    return saved_count + updated_count


async def main():
    """Fonction principale."""
    try:
        # 1. Récupérer données GW2 API
        professions_data = await fetch_gw2_professions()
        specs_data = await fetch_gw2_specializations()
        
        if not professions_data:
            print("\n❌ Aucune profession récupérée!")
            return
        
        # 2. Sauvegarder professions
        prof_count = save_professions(professions_data)
        
        # 3. Créer map des professions (nom → objet)
        session = Session()
        all_professions = session.query(Profession).all()
        professions_map = {p.name: p for p in all_professions}
        session.close()
        
        # 4. Sauvegarder elite specs
        spec_count = 0
        if specs_data:
            spec_count = save_elite_specializations(specs_data, professions_map)
        
        # 5. Résumé
        print("\n" + "="*50)
        print("✅ INITIALISATION TERMINÉE!")
        print("="*50)
        print(f"📊 Professions en DB: {prof_count}")
        print(f"📊 Elite specs en DB: {spec_count}")
        print(f"🗄️  Base de données: {DB_PATH}")
        print("\n🎉 Données GW2 prêtes pour le moteur d'optimisation!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
