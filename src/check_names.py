"""
Ça arrive souvent : on inverse le champ du nom et du prénom en remplissant les cases.
Ce script permet d'éventuellement repérer (et corriger TODO) de telles erreurs
"""

import pandas as pd
from tabulate import tabulate

class Names():
    """
    A class for validating and checking names against an official French government dataset.

    This class loads a list of valid French names from the French government's open data portal
    and provides methods to verify whether names exist in this reference dataset.

    :param data_url: URL vers le fichier de données CSV à charger
        (par défaut https://www.data.gouv.fr/api/1/datasets/r/30800be0-8b72-4e89-9ecf-58ea7dedfe86)
    :param sep: séparateur du fichier CSV
    :param field_name: Nom de la colonne qui contient les prénoms (par défaut "Prenoms")
    """

    def __init__(self,
                 data_url="https://www.data.gouv.fr/api/1/datasets/r/30800be0-8b72-4e89-9ecf-58ea7dedfe86",
                 sep=";",
                 field_name = "Prenoms"
                ) -> None:
        self.csv_data = pd.read_csv(data_url, sep=sep)
        self.list_of_names = self.csv_data[field_name]

    def check_names(self, names_to_check):
        """Vérifie sur les noms donnés sont dans la liste des prénoms définie
        (par défaut https://www.data.gouv.fr/datasets/prenoms-declares).
        Les noms affichés sont ceux qui ne sont pas présents dans la liste.

        :param participants: Dataframe des noms à vérifier
        """
        missing_names = names_to_check[~names_to_check["Prénom"].isin(self.list_of_names)]
        if len(missing_names) > 0:
            print(tabulate(missing_names[["Prénom", "Nom"]]))
        else:
            print("Tout semble bon ici")

    def get_valid_names(self):
        """Returns the list of valid names from the reference dataset.

        :return: Series of valid names
        """
        return self.list_of_names
