import os
from .utils import get_path

def get_team_names(participants):
    print("Gettings team names...", end=" ")
    output = ""
    unique_teams = participants[['Équipe', 'Trigramme']].drop_duplicates()
    # print(unique_teams)
    for _, row in unique_teams.iterrows():
        output += f"        {row['Trigramme']}/{{{row['Équipe']}}},\n"
    print("Done.")
    return output[:-2]

def generate_template(teams, special, tournoi, env):
    orga = special.get('orga', {})
    if orga:
        teams += ",\n"
    for key in orga:
        teams += f"        {key}/{{{orga[key]}}},\n"
    teams = teams[:-2]  # Remove the last comma and newline

    poules = special.get('poules', [])
    poules_str = ", ".join(poules)

    jury = special.get('jury', [])
    jury_str = ", ".join(jury)

    ifdefinition = ""
    if len(teams) > 0:
        ifdefinition += "\n\\teamstrue"
    if len(poules_str) > 0:
        ifdefinition += "\n\\pouletrue"
    if len(jury) > 0:
        ifdefinition += "\n\\jurytrue"

    template_salle = env.get_template("salles_equipes.tex")
    data = {
        "name": tournoi['name'],
        "year": tournoi['year'],
        "teams": teams,
        "poules": poules_str,
        "jury": jury_str,
        "ifdefinition": ifdefinition
    }
    results = template_salle.render(**data)
    output_dir = get_path("$rootDir/output/salles")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(get_path(os.path.join(output_dir, "salles_equipes.tex")), 'w') as f:
        f.write(results)