"""
Génère les affiches des salles pour le TFJM²
"""
import os
import pandas as pd
from liquid import Environment
from .utils import get_path, create_unexisting_dir, texify

def get_team_names(participants:pd.DataFrame):
    """
    Récupères la liste des noms d'équipes et leurs trigrammes

    :param participants: Dataframe des participant.es
    """
    print("Gettings team names...", end=" ")
    output = ""
    unique_teams = participants[['Équipe', 'Trigramme']].drop_duplicates()
    # print(unique_teams)
    for _, row in unique_teams.iterrows():
        output += f"        {row['Trigramme']}/{{{texify(row['Équipe'])}}},\n"
    print("Done.")
    return output[:-2]

def _template_build_special_strings(special:dict) -> dict:
    """
    Build special room strings from special configuration.

    :param special: Dict containing special room configurations
    :return: Dictionary with formatted strings
    """
    return {
        "poules": ", ".join(special.get('poules', [])) + "%",
        "jury": ", ".join(special.get('jury', [])) + "%",
        "special": ", ".join(special.get('special', [])) + "%"
    }

def _template_build_ifdefinition(teams:str, special_strs:dict) -> str:
    """
    Build LaTeX ifdefinition string based on available content.

    :param teams: Teams string
    :param special_strs: Dictionary of special strings
    :return: ifdefinition string
    """
    ifdefinition = ""
    if len(teams) > 0:
        ifdefinition += "\n\\teamstrue"
    if len(special_strs["poules"]) > 0:
        ifdefinition += "\n\\pouletrue"
    if len(special_strs["jury"]) > 0:
        ifdefinition += "\n\\jurytrue"
    if len(special_strs["special"]) > 0:
        ifdefinition += "\n\\specialtrue"
    return ifdefinition

def generate_template(teams:str, special:dict, tournoi:dict, output_dir:str, env:Environment):
    """
    Génère les salles

    :param teams: String avec les équipes/trigrammes
    :param special: Dict qui contient les éventuelles salles spéciales à générer (cf. doc)
    :param tournoi: Configuration du tournoi
    :param output_dir: Chemin vers le dossier où les fichiers générés seront exportés
    :param env: Environnement du module liquid
    """
    orga = special.get('orga', {})
    if orga:
        teams += ",\n"
    for key in orga:
        teams += f"        {key}/{{{orga[key]}}},\n"
    teams = teams[:-2]  # Remove the last comma and newline

    special_strs = _template_build_special_strings(special)
    ifdefinition = _template_build_ifdefinition(teams, special_strs)

    template_salle = env.get_template("salles_equipes.tex")
    data = {
        "name": tournoi['name'],
        "year": tournoi['year'],
        "teams": teams,
        "poules": special_strs["poules"],
        "jury": special_strs["jury"],
        "special": special_strs["special"],
        "ifdefinition": ifdefinition
    }
    results = template_salle.render(**data)
    output_dir_salles = os.path.join(output_dir, "salles")
    create_unexisting_dir(output_dir_salles)
    with open(get_path(os.path.join(output_dir_salles, "salles_equipes.tex")), 'w', encoding="utf-8") as f:
        f.write(results)
