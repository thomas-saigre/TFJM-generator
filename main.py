import sys, os
import json
import pandas as pd
from liquid import CachingFileSystemLoader, Environment
import shutil

import scripts.generate_latex_badges as badges
from scripts.generate_team_room import get_team_names



def get_path(str):
    return str.replace("$rootDir", os.path.dirname(os.path.realpath(__file__))).replace("$pwd", os.getcwd())



if __name__ == '__main__':
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = get_path("$rootDir/config.json")

    with open(json_path, 'r') as f:
        data = json.load(f)

    env = Environment(
        autoescape = False,
        loader = CachingFileSystemLoader(get_path("$rootDir/template"))
    )

    tournoi = data['tournoi']
    run = data['run']

    df_participants = pd.read_csv( get_path(data['csv']['participants']) )
    df_jury = pd.read_csv( get_path(data['csv']['jury']) )
    df_orga = pd.read_csv( get_path(data['csv']['orga']) )

    if run['badges']:
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

    if run['salles']:
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