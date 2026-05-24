````md id="d8s92"
# 🎓 UniNotes ERP

UniNotes ERP est une plateforme intelligente de gestion universitaire développée avec Django.

L’application permet aux étudiants, enseignants, tuteurs et administrateurs de gérer efficacement les activités académiques à travers une interface moderne, intuitive et dynamique.

---

# 🚀 Fonctionnalités

## 👨‍🎓 Étudiant

- Authentification sécurisée
- Tableau de bord personnalisé
- Consultation des modules inscrits
- Gestion des estimations de notes
- Calcul automatique des moyennes
- Suivi de l’évolution académique
- Notifications intelligentes
- Export PDF du relevé de notes
- Gestion du profil

---

## 👨‍🏫 Enseignant

- Gestion des notes officielles
- Gestion des catégories d’évaluation
- Ajout de remarques pédagogiques
- Consultation des étudiants
- Tableau de bord dédié

---

## 👨‍💼 Tuteur

- Suivi pédagogique des étudiants
- Consultation des performances académiques
- Ajout de remarques et suivis
- Tableau de bord personnalisé

---

## 👨‍💻 Administrateur

- Gestion complète des utilisateurs
- Gestion des modules
- Gestion des catégories d’évaluation
- Gestion des inscriptions académiques

---

# 📊 Fonctionnalités intelligentes

## ✅ Dashboard dynamique

- Statistiques académiques
- Moyenne générale en temps réel
- Visualisation graphique avec Chart.js
- Évolution des notes réelles et estimées
- Notifications académiques

---

## ✅ Gestion académique avancée

- Inscription annuelle des étudiants
- Gestion des modules et coefficients
- Gestion des catégories d’évaluation
- Calcul automatique des moyennes pondérées
- Gestion des notes officielles et estimations

---

## ✅ Gestion des rôles

Interfaces et permissions spécifiques pour :

- Étudiants
- Enseignants
- Tuteurs
- Administrateurs

---

# 🧠 Technologies utilisées

- Python
- Django
- Bootstrap 5
- SQLite
- HTML5
- CSS3
- JavaScript
- Chart.js
- ReportLab

---

# 📂 Structure du projet

```bash
uninotes_erp/
│
├── accounts/
├── catalog/
├── enrollment/
├── templates/
├── static/
├── manage.py
└── requirements.txt
````

---

# ⚙️ Installation

## 1️⃣ Cloner le projet

```bash
git clone <repository_link>
```

---

## 2️⃣ Créer un environnement virtuel

```bash
python -m venv venv
```

---

## 3️⃣ Activer l’environnement virtuel

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 4️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 6️⃣ Créer un super utilisateur

```bash
python manage.py createsuperuser
```

---

## 7️⃣ Lancer le serveur

```bash
python manage.py runserver
```

---

# 📈 Fonctionnalités visuelles

* Courbes d’évolution des notes
* Dashboard responsive
* Cartes statistiques modernes
* Interface utilisateur intuitive
* Design Bootstrap moderne

---

# 🔐 Sécurité & Permissions

* Authentification sécurisée
* Gestion des rôles
* Contrôle d’accès par utilisateur
* Protection des vues sensibles

---

# 🔥 Améliorations futures

* API REST avec Django REST Framework
* Notifications email
* Système IA de recommandation académique
* Dark mode
* Application mobile
* Export Excel
* Analyse prédictive des performances

---

# 👨‍💻 Auteur

Développé par :

sfaxi abir

Dans le cadre d’un projet académique ERP universitaire.

---

# 📜 Licence

Projet développé dans un cadre académique et éducatif.


