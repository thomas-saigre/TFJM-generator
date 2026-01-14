"""
Génère le matériel nécéssaire pour une édition du TFJM²
"""
import sys
import os
import json
import shutil
import pandas as pd
from liquid import CachingFileSystemLoader, Environment
from num2words import num2words

import scripts.generate_latex_badges as badges
import scripts.generate_team_room as rooms
from scripts.utils import get_path


if __name__ == '__main__':
    if len(sys.argv) > 1:
        JSON_PATH = sys.argv[1]
    else:
        JSON_PATH = get_path("$rootDir/config.json")

    with open(JSON_PATH, 'r', encoding="utf-8") as f:
        config = json.load(f)

    template_path = config.get("template_dir", "$rootDir/template")
    template_dir = get_path(template_path)

    env = Environment(
        autoescape = False,
        loader = CachingFileSystemLoader(template_dir)
    )

    tournoi = config['tournoi']
    run = config['run']
    special = config.get('special', {})

    df_participants = pd.read_csv(get_path(config['csv']['participants']))
    df_jury = pd.read_csv(get_path(config['csv']['jury']))
    df_orga = pd.read_csv(get_path(config['csv']['orga']))

    for df in [df_participants, df_jury, df_orga]:
        df["Prénom"] =df["Prénom"].str.capitalize()
        df["Nom"] =df["Nom"].str.capitalize()

    if run.get('badges', False):
        OUTPUT_DIR = get_path("$rootDir/output/badges")
        badges.run(df_participants, df_jury, df_orga, OUTPUT_DIR)
        badges.generate_template(template_dir, tournoi, OUTPUT_DIR, env)

    if run.get('salles', False):
        teams = rooms.get_team_names(df_participants)
        rooms.generate_template(teams, special, tournoi, env)

    if run.get('diplomes', False):

        print("Generating diplome...", end=" ")

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

        template_diplome = env.get_template("diplome_eleve.tex")
        template_diplome_team = env.get_template("diplome_equipe.tex")
        data = {
            "name": tournoi['name'],
            "year": tournoi['year'],
            "date": tournoi['date'],
            "number": num2words(tournoi['number'], lang='fr', to='ordinal').capitalize(),
        }
        results = template_diplome.render(**data)
        OUTPUT_DIR = get_path("$rootDir/output/diplomes")
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        with open(get_path(os.path.join(OUTPUT_DIR, "diplome_eleves.tex")), 'w', encoding="utf-8") as f:
            f.write(results)
        results_team = template_diplome_team.render(**data)
        with open(get_path(os.path.join(OUTPUT_DIR, "diplome_equipe.tex")), 'w', encoding="utf-8") as f:
            f.write(results_team)



        LOGO_SRC = get_path("$rootDir/template/logos")
        LOGO_DEST = os.path.join(OUTPUT_DIR, "logos")
        if os.path.exists(LOGO_DEST):
            shutil.rmtree(LOGO_DEST)
        shutil.copytree(LOGO_SRC, LOGO_DEST)

        SIGNATURE_SRC = get_path("$rootDir/template/logos_and_signature.tex")
        SIGNATURE_DEST = os.path.join(OUTPUT_DIR, "logos_and_signature.tex")
        shutil.copy(SIGNATURE_SRC, SIGNATURE_DEST)

        participants_dest = os.path.join(OUTPUT_DIR, "participants.csv")
        df_eleves.to_csv(participants_dest, index=False)
        team_dest = os.path.join(OUTPUT_DIR, "liste_equipes.csv")
        df_teams.to_csv(team_dest, index=False)

        print("Done.")
