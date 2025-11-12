# Premier League Match Outcome Predictor

This project fetches live Premier League football data from the **Football Web Pages API** and uses basic team statistics to predict match outcomes for all fixtures (first and second legs) in the league.

---

## Features

- Automatically fetches Premier League competition, teams, fixtures, and league table data from the Football Web Pages API.
- Uses a simple heuristic model based on league points and goal difference to predict match outcomes.
- Predicts results for **all fixtures**, including both **first leg and second leg** matches.
- Prints predictions in a clear, readable format.

---

## Requirements

- Python 3.7+
- `requests` library
- `pandas` library

You can install dependencies via pip:

```bash
pip install requests pandas
