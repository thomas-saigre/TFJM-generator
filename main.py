"""
Génère le matériel nécéssaire pour une édition du TFJM²
"""
import sys
import json
import argparse
import pandas as pd
from liquid import CachingFileSystemLoader, Environment

import src.generate_latex_badges as badges
import src.generate_team_room as rooms
import src.generate_diplomas as diplomas
from src.utils import get_path, format_name


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                    prog='TFJM-generator',
                    description='Génère des fichiers utiles pour le TFJM²')

    parser.add_argument('-c', '--config', default=get_path("$rootDir/config.json"), help="Chemin vers le fichier JSON de configuration")
    parser.add_argument('--check-names', default=False, action="store_true", help="Vérifie les prénoms renseignés")

    args = parser.parse_args()
    print(args.config, args.check_names)

    json_path = args.config
    check_names = args.check_names

    with open(json_path, 'r', encoding="utf-8") as f:
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
        df["Prénom"] = df["Prénom"].apply(format_name)
        df["Nom"] = df["Nom"].apply(format_name)

    if run.get('badges', False):
        badges.run(df_participants, df_jury, df_orga, output_dir, check_names=check_names)
        badges.generate_template(template_dir, tournoi, output_dir, env)

    if run.get('salles', False):
        teams = rooms.get_team_names(df_participants)
        rooms.generate_template(teams, special, tournoi, output_dir, env)

    if run.get('diplomes', False):
        diplomas.run(template_dir, df_participants, tournoi, output_dir, env)
