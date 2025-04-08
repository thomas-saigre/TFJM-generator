import pandas as pd
import sys, os

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
    fd = open(os.path.join(outdir, "participants.tex"), "w")
    count = 0
    for _, row in participants.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Équipe {row['Trigramme']}", fd)
        count += 1
    fill(count, fd)
    fd.close()

    fd = open(os.path.join(outdir, "jury.tex"), "w")
    count = 0
    for _, row in jury.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Membre du jury", fd)
        count += 1
    fill(count, fd)
    fd.close()

    fd = open(os.path.join(outdir, "orga.tex"), "w")
    count = 0
    for _, row in orga.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Comité d'organisation/bénévole", fd)
        count += 1
    fill(count, fd)
    fd.close()
    print("Badges generated.")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python generate_latex_badges_tfjm_pandas.py <participants_file> <jury_file> <benevoles_file>")
        sys.exit(1)
    participants = pd.read_csv(sys.argv[1])
    jury = pd.read_csv(sys.argv[2])
    orga = pd.read_csv(sys.argv[3])

    run(participants, jury, orga)