# 💼 JobApply — Suivi de candidatures avec Claude AI

Application Streamlit pour suivre tes candidatures, avec comptes utilisateurs,
connexion securisee, et extraction automatique des infos depuis n'importe
quelle URL d'offre d'emploi via Claude.

---

## ⚡ Installation rapide

### 1. Cloner / dézipper le projet

```bash
cd job-tracker
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copie `.env.example` en `.env` et remplis MongoDB + une cle IA :

```bash
cp .env.example .env
```

Édite `.env` :

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=job_tracker
ANTHROPIC_API_KEY=sk-ant-...
# ou
# GROQ_API_KEY=gsk_...
```

#### 🔑 Obtenir les clés

**MongoDB Atlas (gratuit) :**
1. Va sur [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Crée un compte → New Project → Build a Database (Free tier M0)
3. Crée un user + mot de passe
4. Autorise ton IP (Network Access → Add IP)
5. Copie la connection string (Connect → Drivers → Python)

**Anthropic API :**
1. Va sur [console.anthropic.com](https://console.anthropic.com)
2. API Keys → Create Key
3. Copie la clé dans `.env`

**Groq API :**
1. Va sur [console.groq.com](https://console.groq.com)
2. Crée une API key
3. Copie la clé dans `.env` sous `GROQ_API_KEY`

### 5. Lancer l'application

```bash
streamlit run app.py
```

Ouvre [http://localhost:8501](http://localhost:8501) 🚀

---

## ☁️ Déploiement sur Streamlit Community Cloud

Le projet est maintenant prêt pour Streamlit Cloud : `requirements.txt` est présent, l'entrée de l'application est [app.py](app.py), et les secrets peuvent être lus depuis `st.secrets`.

### 1. Pousser le projet sur GitHub

- Crée un dépôt GitHub pour le projet
- Pousse le code source sans le fichier `.env`
- Vérifie que [ .gitignore ] contient bien `.env`, `venv/` et `.streamlit/secrets.toml`
- Tu peux t'appuyer sur [ .streamlit/secrets.toml.example ](.streamlit/secrets.toml.example) pour remplir les secrets côté Streamlit

### 2. Créer l'application sur Streamlit

1. Va sur [share.streamlit.io](https://share.streamlit.io)
2. Connecte ton compte GitHub
3. Choisis le repo, la branche et le fichier principal `app.py`
4. Lance le déploiement
5. Si Streamlit demande un fichier de config, [ .streamlit/config.toml ](.streamlit/config.toml) est déjà prêt

### 3. Ajouter les secrets dans Streamlit Cloud

Dans l'onglet `Advanced settings` ou `Secrets`, ajoute :

```toml
MONGODB_URI = "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
MONGODB_DB = "job_tracker"
ANTHROPIC_API_KEY = "sk-ant-..."
# ou
# GROQ_API_KEY = "gsk_..."
```

L'application lit maintenant les secrets depuis `st.secrets` en production, et depuis `.env` en local.

### 3 bis. Checklist avant de cliquer sur Deploy

1. Vérifier que `.env` n'est pas versionné
2. Vérifier que MongoDB Atlas accepte les connexions de Streamlit Cloud
3. Vérifier qu'au moins une clé IA est fournie : `ANTHROPIC_API_KEY` ou `GROQ_API_KEY`
4. Vérifier que le fichier principal sélectionné est bien `app.py`
5. Vérifier que les secrets sont collés dans Streamlit et pas dans le dépôt GitHub

### 4. Points d'attention MongoDB Atlas

- Crée un utilisateur MongoDB dédié au projet
- Utilise un mot de passe fort pour la base
- N'utilise pas le compte admin Atlas dans l'app
- Si possible, limite les droits au strict minimum sur la base utilisée
- Vérifie les règles `Network Access` d'Atlas avant mise en prod

---

## 🗂️ Structure du projet

```
job-tracker/
├── app.py                  # Point d'entrée Streamlit
├── requirements.txt
├── .env                    # Variables d'environnement (ne pas committer !)
├── .env.example
├── views/
│   ├── dashboard.py        # Tableau de bord + stats
│   ├── add_job.py          # Ajout d'offre (scraping + Claude)
│   └── list_jobs.py        # Liste, modification, suppression
└── utils/
    ├── auth.py             # Connexion, inscription, session
    ├── db.py               # Connexion MongoDB
    ├── scraper.py          # Scraping URL
    ├── extractor.py        # Extraction via Claude API
    └── jobs.py             # CRUD candidatures
```

---

## 🔄 Flux d'utilisation

1. **Creer un compte** ou **se connecter**
2. **Ajouter une offre** : colle l'URL d'un poste (LinkedIn, WTTJ, Indeed…)
3. **L'IA analyse** : scrape la page + extrait les infos automatiquement
4. **Verifier** : modifie si besoin dans le formulaire pre-rempli
5. **Sauvegarder** : chaque candidature est associee au compte connecte
6. **Suivre** : change le statut au fil du temps (A postuler → Postule → Entretien → Accepte/Refuse)

---

## 📌 Notes

- Le scraping fonctionne sur la plupart des jobboards publics (WTTJ, Indeed, LinkedIn public, etc.)
- Certains sites avec protection anti-bot (Cloudflare) peuvent bloquer le scraping
- Toutes les données restent dans **ta** base MongoDB Atlas

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
