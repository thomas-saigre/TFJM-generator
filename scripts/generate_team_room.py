"""
Génère les affiches des salles pour le TFJM²
"""
import os
import pandas as pd
from liquid import Environment
from .utils import get_path

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
        output += f"        {row['Trigramme']}/{{{row['Équipe']}}},\n"
    print("Done.")
    return output[:-2]

def generate_template(teams:str, special:dict, tournoi:dict, env:Environment):
    """
    Génère les salles

    :param teams: String avec les équipes/trigrammes
    :param special: Dict qui contient les éventuelles salles spéciales à générer (cf. doc)
    :param tournoi: Configuration du tournoi
    :param env: Environnement du module liquid
    """
    orga = special.get('orga', {})
    if orga:
        teams += ",\n"
    for key in orga:
        teams += f"        {key}/{{{orga[key]}}},\n"
    teams = teams[:-2]  # Remove the last comma and newline

    poules = special.get('poules', [])
    poules_str = ", ".join(poules) + "%"

    jury = special.get('jury', [])
    jury_str = ", ".join(jury) + "%"

    special_room = special.get('special', [])
    special_room_str = ", ".join(special_room) + "%"

    ifdefinition = ""
    if len(teams) > 0:
        ifdefinition += "\n\\teamstrue"
    if len(poules_str) > 0:
        ifdefinition += "\n\\pouletrue"
    if len(jury) > 0:
        ifdefinition += "\n\\jurytrue"
    if len(special_room) > 0:
        ifdefinition += "\n\\specialtrue"

    template_salle = env.get_template("salles_equipes.tex")
    data = {
        "name": tournoi['name'],
        "year": tournoi['year'],
        "teams": teams,
        "poules": poules_str,
        "jury": jury_str,
        "special": special_room_str,
        "ifdefinition": ifdefinition
    }
    results = template_salle.render(**data)
    output_dir = get_path("$rootDir/output/salles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(get_path(os.path.join(output_dir, "salles_equipes.tex")), 'w', encoding="utf-8") as f:
        f.write(results)
