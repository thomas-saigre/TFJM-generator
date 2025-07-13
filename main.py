import sys, os
import json
import pandas as pd
from liquid import CachingFileSystemLoader, Environment
import shutil

import scripts.generate_latex_badges as badges
from scripts.generate_team_room import get_team_names
from num2words import num2words



def get_path(str):
    return str.replace("$rootDir", os.path.dirname(os.path.realpath(__file__))).replace("$pwd", os.getcwd())



if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = get_path("$rootDir/config.json")

    with open(json_path, 'r') as f:
        config = json.load(f)

    env = Environment(
        autoescape = False,
        loader = CachingFileSystemLoader(get_path("$rootDir/template"))
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
        output_dir = get_path("$rootDir/output/badges")
        badges.run(df_participants, df_jury, df_orga, output_dir)

        template_badge = env.get_template("generation_badges.tex")
        data = {
            "name": tournoi['name'],
            "year": tournoi['year'],
        }
        results = template_badge.render(**data)
        shutil.copy(get_path("$rootDir/template/tfjm.tdf"), output_dir)
        with open(get_path(os.path.join(output_dir, "badge.tex")), 'w') as f:
            f.write(results)
        logo_src = get_path("$rootDir/template/logos/logo-tfjm.pdf")
        logo_dest = os.path.join(output_dir, "logo-tfjm.pdf")
        shutil.copy(logo_src, logo_dest)

    if run.get('salles', False):
        teams = get_team_names(df_participants)

        orga = special.get('orga', {})
        if orga:
            teams += ",\n"
        for key in orga:
            teams += f"        {key}/{{{orga[key]}}},\n"
        teams = teams[:-2]  # Remove the last comma and newline

        template_salle = env.get_template("salles_equipes.tex")
        data = {
            "name": tournoi['name'],
            "year": tournoi['year'],
            "teams": teams,
        }
        results = template_salle.render(**data)
        output_dir = get_path("$rootDir/output/salles")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(get_path(os.path.join(output_dir, "salles_equipes.tex")), 'w') as f:
            f.write(results)

    if run.get('diplomes', False):

        print("Generating diplome...", end=" ")

        df_eleves = df_participants[df_participants["Type"] == "Élève"]

        # Group participants by team and create a new dataframe for teams
        df_teams = pd.DataFrame(columns=["Équipe", "Nom1", "Prénom1", "Nom2", "Prénom2", "Nom3", "Prénom3", "Nom4", "Prénom4", "Nom5", "Prénom5", "Nom6", "Prénom6", "Nomenc1", "Prénomenc1", "Nomenc2", "Prénomenc2"])

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
        output_dir = get_path("$rootDir/output/diplomes")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(get_path(os.path.join(output_dir, "diplome_eleves.tex")), 'w') as f:
            f.write(results)
        results_team = template_diplome_team.render(**data)
        with open(get_path(os.path.join(output_dir, "diplome_equipe.tex")), 'w') as f:
            f.write(results_team)



        logo_src = get_path("$rootDir/template/logos")
        logo_dest = os.path.join(output_dir, "logos")
        if os.path.exists(logo_dest):
            shutil.rmtree(logo_dest)
        shutil.copytree(logo_src, logo_dest)

        signature_src = get_path("$rootDir/template/logos_and_signature.tex")
        signature_dest = os.path.join(output_dir, "logos_and_signature.tex")
        shutil.copy(signature_src, signature_dest)

        participants_dest = os.path.join(output_dir, "participants.csv")
        df_eleves.to_csv(participants_dest, index=False)
        team_dest = os.path.join(output_dir, "liste_equipes.csv")
        df_teams.to_csv(team_dest, index=False)

        print("Done.")