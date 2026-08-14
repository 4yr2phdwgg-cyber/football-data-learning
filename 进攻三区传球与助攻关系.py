import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


root=r"C:\Users\李小鹏\Desktop\python脚本\项目\open-data-master\data"
filepath1=os.path.join(root,"competitions.json")
with open(filepath1,"r",encoding="utf-8")as f:
    com=json.load(f)
for item in com:
    com_name=item["competition_name"]
    season_name=item["season_name"]
    if com_name=="FIFA World Cup" and season_name=="2022":
        com_id=item["competition_id"]
        saa_id=item["season_id"]
        print(com_id,saa_id)
root1=r"C:\Users\李小鹏\Desktop\python脚本\项目\open-data-master\data\matches"
filepath02=os.path.join(root1,str(com_id))
filepath2=os.path.join(filepath02,f"{str(saa_id)}.json")
with open(filepath2,"r",encoding="utf-8")as f:
    match=json.load(f)
mat_ids=[]
match_sc=[]
for item in match:
    home=item["home_team"]["home_team_name"]
    away=item["away_team"]["away_team_name"]
    if home=="Argentina" or away=="Argentina":
        mid=item["match_id"]
        mat_ids.append(mid)
        match_sc.append({
            "match_id":mid,
            "home":home,
            "away":away,
            "score": f"{item['home_score']}:{item['away_score']}",
            "stage":item["competition_stage"]["name"]
        })
print(len(mat_ids))
events={}
root2=r"C:\Users\李小鹏\Desktop\python脚本\项目\open-data-master\data\events"
for mid in mat_ids:
    filepath3=os.path.join(root2,f"{mid}.json")
    with open(filepath3,"r",encoding="utf-8")as f:
        event=json.load(f)
        events[mid]=event




def parse_events_to_df(events_list, match_id):
    """将单场比赛的事件列表转换为扁平 DataFrame"""
    rows = []
    for ev in events_list:
        # 基础字段
        row = {
            'match_id': match_id,
            'period': ev.get('period'),
            'minute': ev.get('minute'),
            'second': ev.get('second'),
            'team': ev.get('team', {}).get('name'),
            'player': ev.get('player', {}).get('name'),
            'type': ev.get('type', {}).get('name'),
            'possession': ev.get('possession'),
            'possession_team': ev.get('possession_team', {}).get('name'),
            'location_x': ev.get('location', [None, None])[0],
            'location_y': ev.get('location', [None, None])[1],
        }
        
        # 传球细节
        pass_info = ev.get('pass', {})
        if pass_info:
            row['pass_outcome'] = pass_info.get('outcome', {}).get('name')
            row['pass_recipient'] = pass_info.get('recipient', {}).get('name')
            end_loc = pass_info.get('end_location', [None, None])
            row['pass_end_x'] = end_loc[0]
            row['pass_end_y'] = end_loc[1]
            row['pass_length'] = pass_info.get('length')
            row['pass_cross'] = pass_info.get('cross')
            row['pass_switch'] = pass_info.get('switch')
            row['pass_goal_assist'] = pass_info.get('goal_assist')
        
        # 射门细节
        shot_info = ev.get('shot', {})
        if shot_info:
            row['shot_outcome'] = shot_info.get('outcome', {}).get('name')
            row['shot_xg'] = shot_info.get('statsbomb_xg')
            row['shot_body_part'] = shot_info.get('body_part', {}).get('name')
            row['shot_technique'] = shot_info.get('technique', {}).get('name')
        
        # 盘带
        dribble_info = ev.get('dribble', {})
        if dribble_info:
            row['dribble_outcome'] = dribble_info.get('outcome', {}).get('name')
        
        # 防守
        duel_info = ev.get('duel', {})
        if duel_info:
            row['duel_type'] = duel_info.get('type', {}).get('name')
            row['duel_outcome'] = duel_info.get('outcome', {}).get('name')
        
        clearance_info = ev.get('clearance', {})
        if clearance_info:
            row['clearance_body_part'] = clearance_info.get('body_part', {}).get('name')
        
        interception_info = ev.get('interception', {})
        if interception_info:
            row['interception_outcome'] = interception_info.get('outcome', {}).get('name')
        
        # 犯规与纪律
        foul_committed = ev.get('foul_committed', {})
        if foul_committed:
            row['foul_type'] = foul_committed.get('type', {}).get('name')
            row['card'] = foul_committed.get('card', {}).get('name')
        
        rows.append(row)
    
    return pd.DataFrame(rows)

# 合并所有比赛
all_dfs = []
for mid, events_list in events.items():
    df = parse_events_to_df(events_list, mid)
    all_dfs.append(df)
 
df_all = pd.concat(all_dfs, ignore_index=True)
action_types = ['Pass', 'Shot', 'Dribble', 'Ball Recovery', 'Duel', 
                'Clearance', 'Interception', 'Block', 'Foul Committed',
                'Pressure', '50/50', 'Offside', 'Bad Behaviour']


df_clean=df_all[df_all['type'].isin(action_types)].copy()

def analyze_final_third_passes(df_clean, team, x_threshold=80):
    
    # 筛选本队所有传球
    passes = df_clean[(df_clean['team'] == team) & (df_clean['type'] == 'Pass')]
    
    # 定义成功传球（与 team_stats 一致）
    success_mask = (passes['pass_outcome'].isna() | 
                    passes['pass_outcome'].str.contains('Complete', na=False))
    successful = passes[success_mask]
    
    # 进攻三区传球：终点 x 坐标 >= 阈值
    final_third = successful[successful['pass_end_x'] >= x_threshold]
    ft_counts = final_third.groupby('match_id').size().reset_index(name='final_third_passes')
    
    # 助攻传球（pass_goal_assist 为 True）
    assists = passes[passes['pass_goal_assist'] == True]
    ast_counts = assists.groupby('match_id').size().reset_index(name='assists')
    
    # 合并结果，没有的填 0
    result = pd.merge(ft_counts, ast_counts, on='match_id', how='outer').fillna(0)
    result[['final_third_passes', 'assists']] = result[['final_third_passes', 'assists']].astype(int)
    
    # 按进攻三区传球数降序排列
    result = result.sort_values('final_third_passes', ascending=False).reset_index(drop=True)
    
    return result

ft_result = analyze_final_third_passes(df_clean, "Argentina", x_threshold=80)
ft_result.to_csv(os.path.join(r'C:\Users\李小鹏\Desktop\python脚本\项目','final_third_passes_assists.csv'), index=False, encoding='utf-8')
plt.figure(figsize=(8, 6))
plt.scatter(ft_result['final_third_passes'], ft_result['assists'])
plt.xlabel('Final Third Passes')
plt.ylabel('Assists')
plt.title('Argentina - Final Third Passes vs Assists')
plt.tight_layout()
plt.savefig(os.path.join(r'C:\Users\李小鹏\Desktop\python脚本\项目', 'final_third_vs_assists.png'), dpi=150)
plt.show()

