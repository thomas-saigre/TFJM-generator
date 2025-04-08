import pandas as pd
import sys, os

PRENOM, NOM = 0, 1

def formatName(nom, type_nom):
    if type_nom == PRENOM:
        return nom.title()
    return nom.upper()

def latexiser(prenom, nom, role, fd):
    fd.write("\\confpin{" + formatName(prenom, PRENOM) + " " + formatName(nom, NOM) + "}{" + role + "}\n")

def run(participants, jury, orga, outdir="."):
    print("Generating badges...", end ="")
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    fd = open(os.path.join(outdir, "participants.tex"), "w")
    for _, row in participants.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Équipe {row['Trigramme']}", fd)
    fd.close()

    fd = open(os.path.join(outdir, "jury.tex"), "w")
    for _, row in jury.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Membre du jury", fd)
    fd.close()

    fd = open(os.path.join(outdir, "orga.tex"), "w")
    for _, row in orga.iterrows():
        latexiser(row['Prénom'], row['Nom'], f"Comité d'organisation/bénévole", fd)
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