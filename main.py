import sys, os
import json
import pandas as pd
from liquid import CachingFileSystemLoader, Environment
import shutil

import scripts.generate_latex_badges as badges



def get_path(str):
    return str.replace("$rootDir", os.path.dirname(os.path.realpath(__file__))).replace("$pwd", os.getcwd())



def generate_badges(data, output_dir="."):
    participants = pd.read_csv( get_path(data['participants']) )
    jury = pd.read_csv( get_path(data['jury']) )
    orga = pd.read_csv( get_path(data['orga']) )

    badges.run(participants, jury, orga, output_dir)


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

    if run['badges']:
        outpur_dir = get_path("$rootDir/output/badges")
        generate_badges(data['csv'], output_dir=outpur_dir)
        template_badge = env.get_template("generation_badges.tex")
        data = {
            "name": tournoi['name'],
            "year": tournoi['year'],
        }
        results = template_badge.render(**data)
        shutil.copy(get_path("$rootDir/template/tfjm.tdf"), outpur_dir)
        with open(get_path(os.path.join(outpur_dir, "badge.tex")), 'w') as f:
            f.write(results)