import pandas as pd
season_2022 = pd.DataFrame({
    'player_id': [1, 2, 3],
    'season': ['2022']*3,
    'goals': [15, 8, 12],
    'matches': [35, 33, 30]
})

season_2023 = pd.DataFrame({
    'player_id': [1, 2, 4],
    'season': ['2023']*3,
    'goals': [20, 10, 5],
    'matches': [38, 36, 28]
})

season_2024 = pd.DataFrame({
    'player_id': [1, 3, 4],
    'season': ['2024']*3,
    'goals': [18, 14, 8],
    'matches': [34, 32, 30]
})

# 纵向拼接三个赛季
all_seasons = pd.concat([season_2022, season_2023, season_2024], ignore_index=True)
print(all_seasons)

