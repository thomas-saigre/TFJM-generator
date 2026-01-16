"""
Génère le matériel nécéssaire pour une édition du TFJM²
"""
import sys
import json
import pandas as pd
from liquid import CachingFileSystemLoader, Environment

import scripts.generate_latex_badges as badges
import scripts.generate_team_room as rooms
import scripts.generate_diplomas as diplomas
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
    output_path = config.get("output_dir", "$rootDir/output")
    output_dir = get_path(output_path)

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
        badges.run(df_participants, df_jury, df_orga, output_dir)
        badges.generate_template(template_dir, tournoi, output_dir, env)

    if run.get('salles', False):
        teams = rooms.get_team_names(df_participants)
        rooms.generate_template(teams, special, tournoi, output_dir, env)

    if run.get('diplomes', False):
        diplomas.run(template_dir, df_participants, tournoi, output_dir, env)
