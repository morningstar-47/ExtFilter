# File-cleaner

Un utilitaire Python pour la gestion de fichiers par extension.

## Description

File-cleaner est un outil en ligne de commande qui permet de :
- Rechercher des fichiers par extension
- Afficher leur contenu
- Les supprimer en toute sécurité (envoi à la corbeille)
- Analyser la distribution des fichiers par extension dans un répertoire

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/morningstar-47/ExtFilter.git
cd File-cleaner
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Le script propose deux commandes principales :

### 1. Rechercher et gérer des fichiers par extension

```bash
python file_cleaner.py search <répertoire> <extension> [options]
```

**Arguments :**
- `<répertoire>` : Chemin du répertoire à analyser
- `<extension>` : Extension des fichiers à rechercher (avec ou sans le point)

**Options :**
- `-d, --delete` : Supprime les fichiers trouvés (les envoie à la corbeille)
- `-c, --confirm` : Demande confirmation avant chaque action
- `-p, --display` : Affiche le contenu des fichiers trouvés
- `-s, --sort-order [asc|desc|random]` : Définit l'ordre de tri des fichiers (par défaut : asc)

### 2. Analyser la distribution des fichiers par extension

```bash
python file_cleaner.py analyze <répertoire>
```

Cette commande affiche un résumé des types de fichiers présents dans le répertoire, classés par leur nombre.

## Exemples d'utilisation

### Rechercher des fichiers texte et afficher leur contenu
```bash
python file_cleaner.py search ~/Documents txt --display
```

### Rechercher et supprimer des fichiers temporaires avec confirmation
```bash
python file_cleaner.py search ~/Downloads tmp --delete --confirm
```

### Afficher le contenu des fichiers logs dans l'ordre chronologique inverse
```bash
python file_cleaner.py search /var/log log --display --sort-order desc
```

### Analyser les types de fichiers présents dans un répertoire
```bash
python file_cleaner.py analyze ~/Projects
```

## Fonctionnalités

- **Recherche intelligente** : Trouve les fichiers par extension, avec ou sans le point initial
- **Tri flexible** : Affiche les résultats par ordre alphabétique croissant/décroissant ou aléatoire
- **Suppression sécurisée** : Utilise send2trash pour envoyer les fichiers à la corbeille au lieu de les supprimer définitivement
- **Confirmation interactive** : Option pour confirmer chaque action
- **Visualisation du contenu** : Affiche le contenu des fichiers texte
- **Analyse de répertoire** : Compte et affiche la distribution des types de fichiers

## Configuration requise

- Python 3.6 ou supérieur
- Modules Python :
  - click
  - send2trash
  - pathlib

## Tests

Pour exécuter les tests unitaires :

```bash
python -m unittest test_file_cleaner.py
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE.md` pour plus d'informations.

## Auteur

Créé par [Claude-Mops47](https://github.com/morningstar-47)