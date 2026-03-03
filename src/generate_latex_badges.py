"""
Génère les badges pour le TFJM²
"""
import os
import pandas as pd
from liquid import Environment
from .utils import get_path, copy_into, create_unexisting_dir

PRENOM, NOM = 0, 1

def format_name(nom, type_nom):
    """
    Formate un nom sous la forme Prénom NOM

    :param nom: Prénom ou nom
    :param type_nom: Type du nom (PRENOM ou NOM)
    """
    if type_nom == PRENOM:
        return nom.title()
    return nom.upper()

def fill(count, fd):
    """
    Fill remaining slots on the last page with empty names

    :param count: Count of badges already inserted
    :param fd: File descriptor
    """
    while count % 10 != 0:
        latexiser("", "", "", fd)
        count += 1
    return count

def latexiser(prenom, nom, role, fd):
    """
    Génère la ligne de code LaTeX pour dessiner le badge de la personne

    :param prenom: Le prénom de la personne
    :param nom: Son nom
    :param role: Son rôle
    :param fd: File descriptor
    """
    if prenom == "" and nom == "" and role == "":
        fd.write("\\confpin{}{}\n")
    else:
        fd.write("\\confpin{" + format_name(prenom, PRENOM) + " " + format_name(nom, NOM) + "}{" + role + "}\n")

def run(df_participants:pd.DataFrame, df_jury:pd.DataFrame, df_orga:pd.DataFrame, output_dir:str="."):
    """
    Génère les badges

    :param participants: Dataframe des participant.es
    :param jury: Dataframe des membres du jury
    :param orga: Dataframe des orga/bénévoles
    :param outdir: Chemin où les fichiers LaTeX seront exportés
    """
    print("Generating badges...", end =" ")
    output_dir_badges = os.path.join(output_dir, "badges")
    create_unexisting_dir(output_dir_badges)
    with open(
        os.path.join(output_dir_badges, "participants.tex"), "w", encoding="utf-8"
    ) as fd_p, open(
        os.path.join(output_dir_badges, "encadrantes.tex"), "w", encoding="utf-8"
    ) as fd_e:
        count_p = 0
        count_e = 0
        for _, row in df_participants.iterrows():
            if row["Type"] == "Élève":
                latexiser(row['Prénom'], row['Nom'], f"Équipe {row['Trigramme']}", fd_p)
                count_p += 1
            elif row["Type"] == "Encadrant⋅e":
                latexiser(row['Prénom'], row['Nom'], f"Équipe {row['Trigramme']}", fd_e)
                count_e += 1
        fill(count_p, fd_p)
        fill(count_e, fd_e)

    with open(os.path.join(output_dir_badges, "jury.tex"), "w", encoding="utf-8") as fd_j:
        count_j = 0
        for _, row in df_jury.iterrows():
            latexiser(row['Prénom'], row['Nom'], "Membre du jury", fd_j)
            count_j += 1
        fill(count_j, fd_j)

    with open(os.path.join(output_dir_badges, "orga.tex"), "w", encoding="utf-8") as fd_o:
        count_o = 0
        for _, row in df_orga.iterrows():
            latexiser(row['Prénom'], row['Nom'], "Comité d'organisation/bénévole", fd_o)
            count_o += 1
        fill(count_o, fd_o)
    print("Badges generated.")

def generate_template(template_dir:str, tournoi_config:dict, output_dir:str, env:Environment):
    """
    Génère le template LaTeX avec tous les badges

    :param template_dir: Chemin vers le dossier où les fichiers templates sont sauvegardés
    :param tournoi_config: Configuration du tournoi
    :param output_dir: Chemin vers le dossier où les fichiers générés seront exportés
    :param env: Environnement du module liquid
    """
    template_path = os.path.join(template_dir, "generation_badges.tex")
    template_badge = env.get_template(template_path)
    data = {
        "name": tournoi_config['name'],
        "year": tournoi_config['year'],
    }
    output_dir_badges = os.path.join(output_dir, "badges")
    create_unexisting_dir(output_dir_badges)
    results = template_badge.render(**data)
    copy_into(os.path.join(template_dir, "tfjm.tdf"), output_dir_badges)
    with open(get_path(os.path.join(output_dir_badges, "badge.tex")), 'w', encoding="utf-8") as f:
        f.write(results)
    logo_src = get_path(os.path.join(template_dir, "logos/logo-tfjm.pdf"))
    copy_into(logo_src, output_dir_badges)
