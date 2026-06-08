# SAE 2.01 - Projet Application Web

## 🚀 Nom de l'application : Geomed

**Description succincte :** Application d'aide à la décision pour l'installation des médecins en France, basée sur les données de l'API de l'Assurance Maladie (Ameli).

---

## 🗺️ Architecture et Structure des Pages

### 1. Page d'Accueil (`/`)
La page principale est conçue comme un tableau de bord interactif pour guider rapidement le médecin.

*   **Module d'Onboarding (Orientation) :**
    *   Formulaire d'introduction ou questionnaire rapide pour cibler les préférences du médecin (Spécialité, mode d'exercice souhaité, région de prédilection, importance des aides financières).
*   **Carte Interactive :**
    *   Visualisation des zones sous-dotées (déserts médicaux / zones ZIP et ZAC).
    *   Système de filtres et sélection de critères (densité de population, âge moyen de la population, concurrence aux alentours).
*   **Section Suggestions :**
    *   Algorithme de recommandation affichant un "Top 3" des meilleures communes ou régions d'installation selon les critères saisis lors de l'onboarding.

### 2. Page Informations (`/informations`)
Une page statique regroupant les ressources administratives et juridiques indispensables à l'installation.

*   **Cadre légal :** Démarches obligatoires auprès de l'Ordre des Médecins, de la CPAM et de l'URSSAF.
*   **Aides financières :** Explications sur les contrats d'aide (CAIM, COSCOM, etc.) liés aux zones prioritaires.
*   **Procédures :** Guide étape par étape pour l'ouverture ou la reprise d'un cabinet médical.

### 3. Page Données (`/donnees`)
Une page dynamique permettant d'explorer de manière brute la base de données issue de l'API Ameli.

*   **Formulaire de sélection :** Moteur de recherche avancé avec filtres (par département, par spécialité, par année).
*   **Visualisation des données :** Affichage de l'ensemble des données de la base sous forme de tableaux ou de graphiques exportables (ex: nombre de consultations, démographie des professionnels de santé).