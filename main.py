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

    df_participants = pd.read_csv( get_path(config['csv']['participants']) )
    df_jury = pd.read_csv( get_path(config['csv']['jury']) )
    df_orga = pd.read_csv( get_path(config['csv']['orga']) )

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

    if run.get('salles', False):
        teams = get_team_names(df_participants)

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

        print("Generating diplome... Warning : the template contains logos thath can change from year to year and from city. Please check the template before running ;)", end=" ")

        df_encadrant = df_participants[df_participants["Date de naissance"] == "Encandrant⋅e"]
        df_eleves = df_participants[df_participants["Date de naissance"] != "Encandrant⋅e"]

        template_diplome = env.get_template("diplome_eleve.tex")
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
        logo_src = get_path("$rootDir/template/logos")
        logo_dest = os.path.join(output_dir, "logos")
        if not os.path.exists(logo_dest):
            os.symlink(logo_src, logo_dest)

        participants_dest = os.path.join(output_dir, "participants.csv")
        df_eleves.to_csv(participants_dest, index=False)

        print("Done.")