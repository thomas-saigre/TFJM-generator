import pandas as pd
import sys, os
from .utils import get_path, copy_into

PRENOM, NOM = 0, 1

def formatName(nom, type_nom):
    if type_nom == PRENOM:
        return nom.title()
    return nom.upper()

def fill(count, fd):
    # Fill remaining slots on the last page with empty names
    while count % 10 != 0:
        latexiser("", "", "", fd)
        count += 1
    return count

def latexiser(prenom, nom, role, fd):
    if prenom == "" and nom == "" and role == "":
        fd.write("\\confpin{}{}\n")
    else:
        fd.write("\\confpin{" + formatName(prenom, PRENOM) + " " + formatName(nom, NOM) + "}{" + role + "}\n")

def run(participants, jury, orga, outdir="."):
    print("Generating badges...", end =" ")
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    fd_p = open(os.path.join(outdir, "participants.tex"), "w")
    fd_e = open(os.path.join(outdir, "encadrantes.tex"), "w")
    count_p = 0
    count_e = 0
    for _, row in participants.iterrows():
        if row["Type"] == "Élève":
            latexiser(row['Prénom'], row['Nom'], f"Équipe {row['Trigramme']}", fd_p)
            count_p += 1
        elif row["Type"] == "Encadrant⋅e":
            latexiser(row['Prénom'], row['Nom'], f"Équipe {row['Trigramme']}", fd_e)
            count_e += 1
    fill(count_p, fd_p)
    fill(count_e, fd_e)
    fd_p.close()
    fd_e.close()

    fd_j = open(os.path.join(outdir, "jury.tex"), "w")
    count_j = 0
    for _, row in jury.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Membre du jury", fd_j)
        count_j += 1
    fill(count_j, fd_j)
    fd_j.close()

    fd_o = open(os.path.join(outdir, "orga.tex"), "w")
    count_o = 0
    for _, row in orga.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Comité d'organisation/bénévole", fd_o)
        count_o += 1
    fill(count_o, fd_o)
    fd_o.close()
    print("Badges generated.")

def generate_template(template_dir, tournoi_config, output_dir, env):
    template_path = os.path.join(template_dir, "generation_badges.tex")
    template_badge = env.get_template(template_path)
    data = {
        "name": tournoi_config['name'],
        "year": tournoi_config['year'],
    }
    results = template_badge.render(**data)
    copy_into(os.path.join(template_dir, "tfjm.tdf"), output_dir)
    with open(get_path(os.path.join(output_dir, "badge.tex")), 'w') as f:
        f.write(results)
    logo_src = get_path(os.path.join(template_dir, "logos/logo-tfjm.pdf"))
    copy_into(logo_src, output_dir)
    pass

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python generate_latex_badges_tfjm_pandas.py <participants_file> <jury_file> <benevoles_file>")
        sys.exit(1)
    participants = pd.read_csv(sys.argv[1])
    jury = pd.read_csv(sys.argv[2])
    orga = pd.read_csv(sys.argv[3])

    run(participants, jury, orga)