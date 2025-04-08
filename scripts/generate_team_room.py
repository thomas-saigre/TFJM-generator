import pandas as pd

def get_team_names(participants):
    print("Gettings team names...", end=" ")
    output = ""
    unique_teams = participants[['Equipe', 'Trigramme']].drop_duplicates()
    # print(unique_teams)
    for _, row in unique_teams.iterrows():
        output += f"        {row['Trigramme']}/{{{row['Equipe']}}},\n"
    print("Done.")
    return output[:-2]