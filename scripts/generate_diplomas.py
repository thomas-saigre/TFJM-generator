"""
Génère les diplômes pour le TFJM²
"""
import os
import shutil
import pandas as pd
from liquid import Environment
from num2words import num2words
from .utils import get_path, create_unexisting_dir, export_df

def treat_dataframes(df_participants:pd.DataFrame):
    """
    Process participant dataframe and create two separate dataframes for students and teams.

    :param df_participants: Description
    :type df_participants: pd.DataFrame

    :return: A tuple containing two dataframes, df_eleves and df_teams
                - df_eleves: Dataframe of all students (filtered by Type == "Élève")
                - df_teams: Dataframe with one row per team, containing team name, up to 6 students
                            with their names/first names, and up to 2 mentors with their names/first names
    :rtype: tuple[pd.DataFrame, pd.DataFrame]
    """
    df_eleves = df_participants[df_participants["Type"] == "Élève"]

    # Group participants by team and create a new dataframe for teams
    df_teams = pd.DataFrame(columns=["Équipe", "Nom1", "Prénom1", "Nom2", "Prénom2", "Nom3", "Prénom3",
                                               "Nom4", "Prénom4", "Nom5", "Prénom5", "Nom6", "Prénom6",
                                               "Nomenc1", "Prénomenc1", "Nomenc2", "Prénomenc2"])

    for team, members in df_participants.groupby("Équipe"):
        team_data = {"Équipe": team}
        students = members[members["Type"] == "Élève"]
        mentors = members[members["Type"] != "Élève"]

        # Add student names (up to 6)
        for i, (_, student) in enumerate(students.iterrows(), start=1):
            team_data[f"Nom{i}"] = student["Nom"]
            team_data[f"Prénom{i}"] = student["Prénom"]

        # Add mentor names (up to 2)
        for i, (_, mentor) in enumerate(mentors.iterrows(), start=1):
            team_data[f"Nomenc{i}"] = mentor["Nom"]
            team_data[f"Prénomenc{i}"] = mentor["Prénom"]

        df_teams = pd.concat([df_teams, pd.DataFrame([team_data])], ignore_index=True)
    df_teams = df_teams.fillna("")

    return df_eleves, df_teams

def generate_diplomas_file(name:str, data:dict, output_dir:str, env:Environment):
    """
    Génère le fichier LaTeX des diplômes

    :param name: Type du diplôme (diplome_eleve ou diplome_equipe)
    :type name: str
    :param data: données à inclure dans le diplôme
    :type data: dict
    :param output_dir: chemin où le fichier sera exporté
    :type output_dir: str
    :param env: Environnement du module liquid
    :type env: Environment
    """
    template = env.get_template(f"{name}.tex")
    results = template.render(**data)
    create_unexisting_dir(output_dir)
    with open(get_path(os.path.join(output_dir, f"{name}.tex")), 'w', encoding="utf-8") as f:
        f.write(results)

def copy_files(template_dir:str, output_dir:str):
    """
    Copie tous les fichiers nécessaires dans le dossier d'output

    :param template_dir: Chemin vers le dossier template
    :type template_dir: str
    :param output_dir: Chemin vers le dossier d'output
    :type output_dir: str
    """
    logo_src = os.path.join(template_dir, "logos")
    logo_dest = os.path.join(output_dir, "logos")
    if os.path.exists(logo_dest):
        shutil.rmtree(logo_dest)
    shutil.copytree(logo_src, logo_dest)

    signature_src = os.path.join(template_dir, "logos_and_signature.tex")
    signature_dest = os.path.join(output_dir, "logos_and_signature.tex")
    shutil.copy(signature_src, signature_dest)


def run(template_dir:str, df_participants:pd.DataFrame, tournoi:dict, output_dir:str, env:Environment):
    """
    Génère les fichiers LaTeX pour les diplômes, ainsi que les fichiers CSV

    :param template_dir: chemin vers le dossier template
    :type template_dir: str
    :param df_participants: Dataframe avec la liste des participant.es
    :type df_participants: pd.DataFrame
    :param tournoi: Dictionnaire avec les données du tournoi
    :type tournoi: dict
    :param output_dir: Chemin du dossier d'output
    :type output_dir: str
    :param env: Environnement liquid
    :type env: Environment
    """
    print("Generating diplome...", end=" ")

    output_dir_diplomes = os.path.join(output_dir, "diplomes")
    df_eleve, df_teams = treat_dataframes(df_participants)
    data = {
        "name": tournoi['name'],
        "year": tournoi['year'],
        "date": tournoi['date'],
        "number": num2words(tournoi['number'], lang='fr', to='ordinal').capitalize(),
    }

    generate_diplomas_file("diplome_eleve", data, output_dir_diplomes, env)
    generate_diplomas_file("diplome_equipe", data, output_dir_diplomes, env)

    copy_files(template_dir, output_dir_diplomes)

    export_df(df_eleve, output_dir_diplomes, "participants.csv")
    export_df(df_teams, output_dir_diplomes, "liste_equipes.csv")

    print("Done.")
