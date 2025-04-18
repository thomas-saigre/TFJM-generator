# TFJM²


Génération automatiques des badges, affiches et diplômes pour le TFJM².


## Requirements

Pour faire tourner les codes, il est nécessaire d'avoir Python, et les packages suivants :
- [`pandas`](https://pypi.org/project/pandas/)
- [`python-liquid`](https://pypi.org/project/python-liquid/)
- [`num2words`](https://pypi.org/project/num2words/)


## Usage

Toute la configuration se faire dans le fichier [`config.json`](config.json), dont voici un exemple :

```json
{
    "csv":
    {
        "participants": "$rootDir/csv/participants.csv",
        "jury": "$rootDir/csv/jury.csv",
        "orga": "$rootDir/csv/orga.csv"
    },
    "run":
    {
        "badges": false,
        "salles": false,
        "diplomes": true
    },
    "tournoi":
    {
        "name": "Strasbourg",
        "year": 2025,
        "number": 15,
        "date": "26 - 27 avril 2025"
    }
}
```

Les champs à remplir avec les fichiers de données au format CSV sont les suivants :
- `csv.participants` : chemin vers le fichier CSV contenant la liste des participants, celle qui est obtenue depuis la plateforme [inscription.tfjm.org](https://inscription.tfjm.org/),
- `csv.jury` : chemin vers le fichier CSV contenant la liste des jurys. Celle la, il faut peut être que vous la fasisez à la main, le fichier doit contenir au moins les colonnes `Nom` et `Prénom`,
- `csv.orga` : chemin vers le fichier CSV contenant la liste des organisateurs/bénévoles. Ce fichier aussi devra être fait à la main, il doit contenir au moins les colonnes `Nom` et `Prénom`.

La quantité `$rootDir` est une variable qui sera remplacée par le chemin vers le dossier contenant le script Python `main.py`.

Pour dire au programme quels fichiers générer, il faut remplir la section `run` :

- `run.badges` : si `true`, le code va générer les badges pour les participants, jurys et organisateurs,
- `run.salles` : si `true`, le code va générer les affiches pour les salles,
- `run.diplomes` : si `true`, le code va générer les diplômes pour les participants.

Enfin, les informations sur le tournoi sont à remplir dans la section `tournoi` :
- `tournoi.name` : nom du tournoi (ex : Strasbourg),
- `tournoi.year` : année du tournoi (ex : 2025),
- `tournoi.number` : numéro de l'édition du tournoi (ex : 15), cette quantité sera convertie en ordinal sur le diplôme (ex : 15 -> Quinzième)
- `tournoi.date` : date du tournoi (ex : 26 - 27 avril 2025).


## Usage

Pour faire tourner le code, il suffit de lancer le script Python `main.py` :

```bash
python3 main.py [config.json]
```
L'argument optionnel est le chemin vers le fichier de configuration, par défaut il s'agit de `config.json` dans le même dossier que le script.


## Fichiers générés

Tous les fichiers générés seront placés dans le dossier `output`, qui sera créé automatiquement si il n'existe pas.
Chaque élément généré sera placé dans un sous-dossier, qui sera nommé selon le type de fichier :

- `badges` : un code LaTeX qui contient tous les badges pour les participants, jurys et organisateurs. Si la page n'est pas complète, elle est automatiquement complétée par des badges vides, qui pourraient servir.
- `diplomes` : deux codes LaTeX sont générés, un pour tous les élèves (nominatifs), et un pour chacune des équipes (avec les noms des élèves et des encadrants).
- `salles` : un code LaTeX qui contient toutes les affiches pour chacune des équipes, à afficher devant les salles.


## Personalisation

Il est tout à fait possible de personnalier les fichiers à générer, en modifiant les fichiers de template qui se trouvent dans le dossier [`template`](template).

> [!WARNING]
> Pour les templates LaTeX, il faut faire attention aux `{`, `}` et `%`, qui sont aussi des caractères utilisés par Python-Liquid pour générer à partir de templates.
> En particulier, il ne faut par qu'il y ait `{%` dans le template.

### Badges

Il y a deux fichiers qui peuvent être personalisés :
- [`tfjm.tdf`](template/tfjm.tdf) : ce fichier contient les paramètres du badge, pour changer la tailles de ceux-ci, il faut modifier la ligne `ticketSize` (les paramètres sont en mm),
- [`generation_badges.tex`](template/generation_badges.tex) pour modifier le contenu des badges, dans la macro `\ticketdefault`.


### Affiches pour les salles

Le fichier template est [`salles_equipes.tex`](template/salles_equipes.tex).
Pour modifier le contenu des affiches, il suffit de modifier le contenu de l'environnement `tikzpicture`.
La macro `\team` contient le trigramme de l'équipe, et `\name` le nom complet de l'équipe.


### Diplômes

Il y a deux fichiers de template :
- [`diplome_eleve.tex`](template/diplome_eleve.tex) : ce fichier contient le template pour les diplômes nominatif.
- [`diplome_equipe.tex`](template/diplome_equipe.tex) : ce fichier contient le template pour les diplômes d'équipe.

Pour ces deux fichiers, si vous compilez le template directement, ça devrait fonctionner avec les fichiers d'exemple présents dans le dossier.
Pour que ce soit plus rapide, vous pouvez décommenter la ligne `% \dtlbreak`, pour ne faire que la première page.
Si il y a beaucoup de participantes et participants, ça peut prendre un peu de temps pour compiler le LaTeX.


Il y a aussi le fichier [`logos_and_signature.tex`](template/logos_and_signature.tex) qui contient la disposition des logos des partenaires (dans le template, ce sont ceux de Strasbourg).
(Petit conseil : si vous arrivez à trouver des logos au format vectoriel, c'est mieux, il n'y aura pas de soucis de qualité d'impression.)

Suivant qui est/sont président/e/s du jury, vous pourrez aussi avoir à modifier le petit texte à la fin de ce fichier (par défaut, ça prend en compte tous les cas possibles).
