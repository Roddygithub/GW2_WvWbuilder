# Politique de sécurité

## Signalement des vulnérabilités

Si vous découvrez une vulnérabilité de sécurité dans ce projet, merci de nous en faire part de manière responsable en suivant ces étapes :

1. **Ne créez pas d'issue publique** - Cela pourrait exposer les utilisateurs à des risques.
2. **Contactez-nous en privé** - Envoyez un email à security@example.com avec les détails de la vulnérabilité.
3. **Attendez notre réponse** - Nous vous répondrons dans les 48 heures pour vous accuser réception de votre signalement.
4. **Coordonnez la divulgation** - Nous travaillerons avec vous pour corriger la vulnérabilité et coordonner une divulgation responsable aux utilisateurs.

## Bonnes pratiques de sécurité

### Pour les contributeurs
- Ne committez jamais de données sensibles (mots de passe, clés API, etc.) dans le dépôt
- Utilisez des variables d'environnement pour les informations sensibles
- Tenez à jour vos dépendances pour inclure les correctifs de sécurité
- Signalez toute vulnérabilité que vous pourriez découvrir

### Pour les utilisateurs
- Utilisez toujours la dernière version stable du logiciel
- Ne partagez pas vos jetons d'accès ou informations d'identification
- Signalez tout comportement suspect ou vulnérabilité découverte

## Sécurité des dépendances

Nous utilisons plusieurs outils pour maintenir la sécurité du projet :

- **Dependabot** : Mise à jour automatique des dépendances vulnérables
- **CodeQL** : Analyse statique du code pour détecter les vulnérabilités potentielles
- **Snyk** : Analyse des vulnérabilités dans les dépendances

## Politique de mise à jour de sécurité

Les mises à jour de sécurité critiques sont traitées en priorité et des correctifs sont généralement publiés dans les 72 heures suivant la découverte de la vulnérabilité.
