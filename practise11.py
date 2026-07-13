import os
import pandas as pd

players = pd.DataFrame({
    'player_id': [1, 2, 3, 4, 5],
    'name': ['登贝莱', '杜埃', 'K77', '巴尔克拉', '贡萨洛'],
    'position': ['RW', 'CM', 'LW', 'CB', 'ST'],
    'team': ['巴黎', '巴黎', '巴黎', '巴黎', '巴黎']
})

salaries = pd.DataFrame({
    'player_id': [1, 2, 4, 5, 6],
    'salary_weekly': [250000, 80000, 60000, 120000, 50000],  # 周薪，欧元
    'market_value': [85, 25, 35, 50, 10]  # 身价，百万欧元
})

contracts = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'contract_end': ['2025', '2027', '2026', '2025'],
    'release_clause': [150, 40, 80, 45]  # 违约金，百万欧元
})
contracts_diff=contracts.rename(columns={'players_id':'id'})

inner_merged=pd.merge(players,salaries,on='player_id',how='inner')
print(f"内连接结果共({len(inner_merged)})人")
print(inner_merged[['name','salary_weekly','market_value']])
right_merged=pd.merge(players,contracts,right_on='id',left_on='player_id',how='right')
right_merged=right_merged.drop(columns=['id'])
print(f"\n右连接结果共({len(right_merged)})人")
print(right_merged[['name','contract_end','release_clause']])
full_merged=pd.merge(inner_merged,contracts,right_on='id',left_on='player_id',how='inner')
full_merged=full_merged.drop(columns=['id'])
print(full_merged[['name','market_value','contract_end','release_clause']])
salaries2=salaries.copy()
salaries2['team']=['巴黎', '巴黎', '巴黎', '巴黎', '马赛']
merged=pd.merge(
    players,salaries2,
    on='player_id',how='left',
    suffixes=('_base','_new')
)
print(merged[['player_id','team_base','team_new']])
