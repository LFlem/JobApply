# 💼 JobApply — Suivi de candidatures intelligent

**Simplifiez votre recherche d'emploi avec l'extraction automatique d'offres et un suivi centralisé de vos candidatures.**

JobApply est une plateforme moderne de gestion de candidatures qui sauve du temps en automatisant l'extraction des informations des offres d'emploi. Au lieu de recopier manuellement les détails d'une annonce, importez simplement l'URL et laissez l'IA faire le travail.

---

## 🎯 Pourquoi JobApply ?

### 📊 Suivi organisé
- Centralisez toutes vos candidatures en un seul endroit
- Visualisez votre pipeline avec un tableau de bord intuitif
- Suivez les statuts : À postuler → Postulé → Entretien → Accepté/Refusé

### ⚡ Extraction automatique
- Collez simplement l'URL d'une offre d'emploi
- Claude AI analyse automatiquement la page et extrait :
  - Titre du poste
  - Entreprise
  - Localisation
  - Type de contrat
  - Salaire
  - Compétences requises
  - Avantages

### 🔒 Sécurité et confidentialité
- Authentification sécurisée par compte utilisateur
- Chaque utilisateur accède uniquement à ses propres candidatures
- Données hébergées en base de données privée
- Session avec timeout automatique après inactivité

### 🎨 Interface intuitive
- Design moderne avec thème clair/sombre
- Navigation fluide et épurée
- Statistiques en temps réel

---

## ✨ Fonctionnalités principales

### 1. Tableau de bord
- Vue d'ensemble de votre recherche d'emploi
- Statistiques clés : total de candidatures, répartition par statut
- Pipeline visuel avec barres de progression
- Dernières candidatures en aperçu

### 2. Ajouter une offre
- **Mode automatique** : collez une URL, l'IA extrait tout
- **Mode manuel** : saisissez les informations manuellement
- Support multi-jobboards : LinkedIn, Welcome to the Jungle, Indeed, etc.

### 3. Gestion des candidatures
- Liste complète de toutes vos candidatures
- Filtrage et tri avancés
- Modification des statuts en un clic
- Notes personnelles pour chaque candidature
- Suppression sécurisée

### 4. Système de comptes
- Inscription simple
- Connexion sécurisée
- Persistence de session (restez connecté même après rechargement)
- Déconnexion automatique après 30 minutes d'inactivité

---

## 📈 Cas d'usage

**Pour les candidats actifs en recherche d'emploi :**
- Gérer efficacement plusieurs candidatures simultanément
- Ne rien oublier et suivre le statut de chaque application
- Gagner du temps sur la saisie manuelle des informations

**Pour les professionnels en transition de carrière :**
- Suivre systématiquement toutes ses démarches
- Analyser des tendances (salaires, technologies demandées)
- Maintenir une base de données structurée

---

## 🔧 Architecture technique

JobApply est construite avec :
- **Frontend** : Streamlit (interface web interactive)
- **Backend** : Python
- **Base de données** : MongoDB (stockage sécurisé)
- **IA** : Claude (extraction intelligente des données)
- **Authentication** : Système de cookies sécurisés

---

## 🚀 Démarrer avec JobApply

Voir la documentation d'installation dans la section documentation pour mettre en place votre instance.

---

## 💪 Performance et scalabilité

- Extraction IA instantanée de la plupart des offres d'emploi
- Interface responsive optimisée pour mobile et desktop
- Gestion multi-utilisateurs avec isolation des données
- Session persistante avec persistance de cookie

---

## 🔐 Sécurité en priorité

✅ Authentification utilisateur sécurisée  
✅ Données privées et isolées par utilisateur  
✅ Timeout de session contre les accès non autorisés  
✅ Hash sécurisé des mots de passe (PBKDF2)  
✅ Suppression du cookie de session après déconnexion  

---

## 📋 Feuille de route

- ✅ Extraction automatique d'offres
- ✅ Gestion multi-utilisateurs
- ✅ Pipeline de candidatures
- 🔄 Intégrations jobboards additionnelles
- 🔄 Export de données (CSV/PDF)
- 🔄 Recommandations IA basées sur le profil
- 🔄 Notifications et reminders

---

**JobApply : Parce que trouver un emploi devrait être moins fastidieux.**

2. **Pro**
    - Quota de scraping plus élevé (ex: 200/jour) ou "illimité raisonnable"
    - Suppression des publicités
    - Priorité de traitement et options avancées (export, analytics, etc.)

### Pourquoi ce modèle fonctionne ici

- Le scraping a un coût infra/API (requêtes HTTP + extraction IA)
- Le quota protège techniquement ton service
- La pub finance les utilisateurs gratuits
- Le plan Pro crée une montée en gamme naturelle

---

## 🧩 Comment l'implémenter dans ce projet

Ci-dessous, un plan concret aligné avec la structure actuelle (`utils/`, `views/`, MongoDB).

### 1) Étendre le profil utilisateur

Dans la collection `users`, ajouter des champs de plan et quota:

- `plan`: `free` ou `pro`
- `scrape_limit_daily`: nombre max/jour (ex: 10 pour free, 200 pour pro)
- `scrape_used_daily`: compteur de consommation du jour
- `scrape_day`: date du compteur (ex: `2026-03-18`)
- `ads_enabled`: booléen (true pour free, false pour pro)

Point d'entrée conseillé: logique d'inscription dans `utils/auth.py`.

### 2) Créer un service de quota

Créer un module dédié, par exemple `utils/quota.py`, avec:

- `reset_if_new_day(user_id)`
- `can_scrape(user_id) -> (bool, remaining, message)`
- `consume_scrape(user_id) -> (bool, remaining)`

Règle de base:

1. Si `scrape_day != aujourd'hui`, remettre `scrape_used_daily = 0` et `scrape_day = aujourd'hui`.
2. Autoriser le scraping seulement si `scrape_used_daily < scrape_limit_daily`.
3. Incrémenter le compteur uniquement si le scraping démarre.

### 3) Bloquer avant l'appel scraping

Dans `views/add_job.py`, au clic sur "Scraper et analyser":

1. Récupérer l'utilisateur courant
2. Vérifier le quota via `can_scrape`
3. Si refus: afficher message + CTA "Passer Pro"
4. Si autorisé: appeler `consume_scrape` puis lancer `scrape_job_url(...)`

Important: le quota doit être vérifié **côté backend**, pas uniquement via l'UI.

### 4) Afficher les pubs uniquement pour les comptes free

Dans les vues Streamlit (dashboard, liste, ajout):

- Si `ads_enabled = true`: afficher un bloc sponsorisé (bannière interne, lien affilié, promo partenaire)
- Si `ads_enabled = false`: ne rien afficher

En pratique sur Streamlit, les formats les plus simples sont:

- Encarts sponsorisés internes
- Liens affiliés contextualisés
- Promotion de ton propre plan Pro

### 5) Ajouter une page "Plans & Facturation"

Ajouter une vue dédiée (ex: `views/billing.py`) avec:

- Quota actuel (utilisé / limite)
- Bénéfices du plan Pro
- Bouton d'upgrade (Stripe Checkout recommandé)

Après paiement validé (webhook Stripe):

- mettre `plan = pro`
- augmenter `scrape_limit_daily`
- mettre `ads_enabled = false`

### 6) Sécuriser et tracer

- Ajouter des logs d'usage (`user_id`, date, succès/échec scraping)
- Ajouter un rate-limit anti-abus (IP + user)
- Prévoir un plafond anti-fraude même pour Pro (fair use)

### 7) Respect légal

- Respecter les CGU des sites scrapés
- Ajouter une politique de confidentialité
- Si pub/cookies traçants: gérer consentement RGPD

---

## 🚀 Plan d'exécution (rapide)

1. **Jour 1**: schéma user + service de quota (`utils/quota.py`)
2. **Jour 2**: intégration blocage quota dans `views/add_job.py`
3. **Jour 3**: UI quota + page Plans
4. **Jour 4**: Stripe checkout + webhook upgrade Pro
5. **Jour 5**: instrumentation, messages UX, tests manuels

---

## ✅ Résultat attendu

Après implémentation:

- Les utilisateurs gratuits voient des pubs + une limite de scraping/jour
- Les utilisateurs Pro n'ont pas de pub + un quota plus large
- Ton coût de scraping est maîtrisé
- Tu as un chemin de revenus progressif et clair

---

## 🔐 Données sensibles à sécuriser

Oui, il y a plusieurs données sensibles dans ce projet.

- `MONGODB_URI` : contient l'acces a ta base MongoDB, souvent avec identifiant et mot de passe
- `ANTHROPIC_API_KEY` ou `GROQ_API_KEY` : donne acces a ton fournisseur IA et peut generer des couts
- Les comptes utilisateurs : emails et `password_hash` stockes dans MongoDB
- Les candidatures : notes personnelles, liens, entreprises, statuts et parfois informations privees de suivi RH

### A ne jamais exposer publiquement

- le fichier `.env`
- un éventuel `.streamlit/secrets.toml`
- les captures d'ecran montrant les secrets
- les journaux applicatifs contenant une URI MongoDB complete

### Recommandations minimum

1. Ne commit jamais `.env` ni `.streamlit/secrets.toml`
2. Garde les secrets uniquement dans Streamlit Cloud `Secrets`
3. Utilise une base MongoDB dediee au projet
4. Change les cles si elles ont deja ete partagees ou commitees par erreur
5. Fais des sauvegardes de la base avant ouverture a des utilisateurs reels
