import requests
import pandas as pd
from typing import List

API_KEY = "your_api_key_here"
BASE_URL = "https://api.footballwebpages.co.uk/v2"
HEADERS = {"FWP-API-Key": API_KEY}


def get_competitions():
    url = f"{BASE_URL}/competitions.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_premier_league_competition_id(competitions: List[dict]) -> int:
    for comp in competitions:
        if "Premier League" in comp.get("name", ""):
            return comp["id"]
    raise ValueError("Premier League competition not found.")


def get_teams(comp_id: int):
    url = f"{BASE_URL}/teams.json?comp={comp_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_fixtures(comp_id: int):
    url = f"{BASE_URL}/fixtures-results.json?comp={comp_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_league_table(comp_id: int):
    url = f"{BASE_URL}/league-table.json?comp={comp_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def build_team_stats_df(league_table_json):
    # Convert league table to DataFrame and extract useful stats
    df = pd.DataFrame(league_table_json)
    # Keep relevant columns, rename for clarity
    df = df.rename(columns={
        "team_name": "Team",
        "played": "Played",
        "won": "Won",
        "drawn": "Drawn",
        "lost": "Lost",
        "points": "Points",
        "goals_for": "GF",
        "goals_against": "GA",
        "goal_difference": "GD",
    })
    # Some APIs use different naming - adjust if needed by checking keys
    # Make sure 'Team' column is string for matching
    df["Team"] = df["Team"].astype(str)
    return df


def predict_match_outcome(home_stats, away_stats):
    """
    Simple heuristic:
    - Team with more points is predicted to win.
    - If equal, compare goal difference.
    - If still equal, predict a draw.
    """
    if home_stats["Points"] > away_stats["Points"]:
        return "Home Win"
    elif home_stats["Points"] < away_stats["Points"]:
        return "Away Win"
    else:
        if home_stats["GD"] > away_stats["GD"]:
            return "Home Win"
        elif home_stats["GD"] < away_stats["GD"]:
            return "Away Win"
        else:
            return "Draw"


def main():
    print("Fetching competitions...")
    competitions = get_competitions()
    premier_league_id = get_premier_league_competition_id(competitions)
    print(f"Premier League competition ID: {premier_league_id}")

    print("Fetching teams...")
    teams = get_teams(premier_league_id)
    team_name_to_id = {team["name"]: team["id"] for team in teams}
    print(f"Found {len(teams)} teams.")

    print("Fetching fixtures...")
    fixtures = get_fixtures(premier_league_id)
    print(f"Found {len(fixtures)} fixtures.")

    print("Fetching league table...")
    league_table = get_league_table(premier_league_id)
    team_stats_df = build_team_stats_df(league_table)
    print("League table data loaded.")

    # Make sure team names match between fixtures and league table
    # Mapping may be needed depending on API naming differences

    print("\nPredicting outcomes for all fixtures (1st leg):")
    print(f"{'Home Team':<25} {'Away Team':<25} {'Prediction':<15}")
    print("-" * 65)

    for fixture in fixtures:
        home_team = fixture["home"]["name"]
        away_team = fixture["away"]["name"]

        # Find stats for home and away teams
        home_stats = team_stats_df[team_stats_df["Team"] == home_team]
        away_stats = team_stats_df[team_stats_df["Team"] == away_team]

        if home_stats.empty or away_stats.empty:
            prediction = "Unknown (missing stats)"
        else:
            prediction = predict_match_outcome(home_stats.iloc[0], away_stats.iloc[0])

        print(f"{home_team:<25} {away_team:<25} {prediction:<15}")

    # For second leg predictions, swap home and away teams
    print("\nPredicting outcomes for all fixtures (2nd leg):")
    print(f"{'Home Team':<25} {'Away Team':<25} {'Prediction':<15}")
    print("-" * 65)

    for fixture in fixtures:
        home_team = fixture["away"]["name"]
        away_team = fixture["home"]["name"]

        home_stats = team_stats_df[team_stats_df["Team"] == home_team]
        away_stats = team_stats_df[team_stats_df["Team"] == away_team]

        if home_stats.empty or away_stats.empty:
            prediction = "Unknown (missing stats)"
        else:
            prediction = predict_match_outcome(home_stats.iloc[0], away_stats.iloc[0])

        print(f"{home_team:<25} {away_team:<25} {prediction:<15}")


if __name__ == "__main__":
    main()
