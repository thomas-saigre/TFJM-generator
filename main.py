import sys, os
import json
import pandas as pd
from liquid import CachingFileSystemLoader, Environment
import shutil

import scripts.generate_latex_badges as badges
import scripts.generate_team_room as rooms
from scripts.utils import get_path
from num2words import num2words



if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = get_path("$rootDir/config.json")

    with open(json_path, 'r') as f:
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
        output_dir = get_path("$rootDir/output/badges")
        badges.run(df_participants, df_jury, df_orga, output_dir)
        badges.generate_template(template_dir, tournoi, output_dir, env)

    if run.get('salles', False):
        teams = rooms.get_team_names(df_participants)
        rooms.generate_template(teams, special, tournoi, env)

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