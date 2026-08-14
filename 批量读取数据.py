import json
import os

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

import pandas as pd


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
def status1(df):
    #传球
    passes=df[df['type']=="Pass"]
    total_passes=len(passes)
    passes_completed = passes[passes['pass_outcome'].isna() | 
                              passes['pass_outcome'].str.contains('Complete', na=False)].shape[0]
    
    #射门
    shots=df[df['type']=="Shot"]
    total_shots=len(shots)
    shot_on_target=shots['shot_outcome'].isin(['Saved', 'Goal']).sum()
    goals=(shots['shot_outcome']=="Goal").sum()
    xg_total=shots['shot_xg'].sum()
    #盘带
    dribbles = df[df['type'] == 'Dribble']
    total_dribbles=len(dribbles)
    dribbles_completed=(dribbles['dribble_outcome']=="Complete").sum()
    #防守
    #1.夺回球权
    ball_recoverys=len(df[df['type']=="Ball Recovery"])
    #2.对抗和抢断
    duels=df[df['type']=="Duel"]
    tackles=duels[duels['duel_type']=="Tackle"]
    total_tackles=len(tackles)
    #3.拦截
    interceptions=len(df[df['type']=="Interception"])
    #4.解围
    clearance=len(df[df['type']=="Clearance"])
    #犯规和纪律
    fouls=df[df['type']=="Foul Committed"]
    total_fouls=len(fouls)
    yellows=(fouls['card']=="Yellow Card").sum()
    reds=(fouls['card']=="Red Card").sum()

    stats={
        "passes":total_passes,
        "passes_completed":passes_completed,
        "pass_accuracy":passes_completed/total_passes*100 if total_passes!=0 else 0,
        "shots":total_shots,
        "shot_on_target":shot_on_target,
        "goals":goals,
        "Xg":xg_total,
        "dribbles":total_dribbles,
        "dribbles_completed":dribbles_completed,
        "ball_recoverys":ball_recoverys,
        "duel_successful":total_tackles/len(duels) if len(duels)!=0 else 0,
        'tackles':total_tackles,
        "interceptions":interceptions,
        "clearance":clearance,
        "fouls":total_fouls,
        "yellows":yellows,
        "reds":reds
    }
    return pd.Series(stats)
team_stats=df_clean.groupby(['match_id','team']).apply(status1).reset_index()

   
def calc_player_stats(df):
    # 传球
    passes = df[df['type'] == 'Pass']
    total_passes = len(passes)
    passes_completed = passes[passes['pass_outcome'].isna() | 
                              passes['pass_outcome'].str.contains('Complete', na=False)].shape[0]

    # 射门
    shots = df[df['type'] == 'Shot']
    total_shots = len(shots)
    shot_on_target = shots['shot_outcome'].isin(['Saved', 'Goal']).sum()
    goals = (shots['shot_outcome'] == 'Goal').sum()
    xg_total = shots['shot_xg'].sum()

    # 盘带
    dribbles = df[df['type'] == 'Dribble']
    total_dribbles = len(dribbles)
    dribbles_completed = (dribbles['dribble_outcome'] == 'Complete').sum()
    



    # 防守
    ball_recoveries = len(df[df['type'] == 'Ball Recovery'])
    duels = df[df['type'] == 'Duel']
    tackles = duels[duels['duel_type'] == 'Tackle']
    total_tackles = len(tackles)
    interceptions = len(df[df['type'] == 'Interception'])
    clearances = len(df[df['type'] == 'Clearance'])

    # 犯规与纪律
    fouls = df[df['type'] == 'Foul Committed']
    total_fouls = len(fouls)
    yellows = (fouls['card'] == 'Yellow Card').sum()
    reds = (fouls['card'] == 'Red Card').sum()

    # 接到传球数（作为接球者出现的次数）
    passes_received = len(df[df['pass_recipient'].notna()])  # 在整场比赛里该球员作为接球者的次数

    stats = {
        "passes": total_passes,
        "passes_completed": passes_completed,
        "pass_accuracy": passes_completed / total_passes * 100 if total_passes > 0 else 0,
        "shots": total_shots,
        "shot_on_target": shot_on_target,
        "goals": goals,
        "xg": xg_total,
        "dribbles": total_dribbles,
        "dribbles_completed": dribbles_completed,
        "ball_recoveries": ball_recoveries,
        "duel_successful": total_tackles / len(duels) if len(duels) > 0 else 0,
        "tackles": total_tackles,
        "interceptions": interceptions,
        "clearances": clearances,
        "fouls": total_fouls,
        "yellows": yellows,
        "reds": reds,
        "passes_received": passes_received,
        
    }
    return pd.Series(stats)

argentina_events = df_clean[df_clean['team'] == 'Argentina'].copy()
player_stats = argentina_events.groupby(['match_id', 'player']).apply(calc_player_stats).reset_index()

import numpy as np
import matplotlib.pyplot as plt

match_id=3869685

passes=df_clean[(df_clean['match_id']==match_id)&(df_clean['team']=="Argentina")&(df_clean['type']=="Pass")].copy()
passes=passes.dropna(subset=['player','pass_recipient'])
print(f"有效传球数:{len(passes)}")
print(passes[['player','pass_recipient']])

passes_count=passes.groupby(['player','pass_recipient']).size().reset_index(name="counts")
save=os.path.join(r"C:\Users\李小鹏\Desktop\python脚本\项目","passes_count")
passes_count.to_csv(save,index=False,encoding="utf-8")
pass_m=passes_count.pivot(index='player',columns='pass_recipient',values='counts').fillna(0)
top_players = passes['player'].value_counts().head(11).index.tolist()
pass_m = pass_m.reindex(index=top_players, columns=top_players, fill_value=0)

print(pass_m)
player_positions = passes.groupby('player').agg(
    avg_x=('location_x', 'mean'),
    avg_y=('location_y', 'mean')
).reindex(top_players)

# 在画球员之前，先画球场线
def draw_pitch(ax):
    # 边线
    ax.plot([0, 0], [0, 80], 'black', linewidth=2)
    ax.plot([0, 120], [80, 80], 'black', linewidth=2)
    ax.plot([120, 120], [80, 0], 'black', linewidth=2)
    ax.plot([120, 0], [0, 0], 'black', linewidth=2)
    # 中线
    ax.plot([60, 60], [0, 80], 'black', linewidth=2)
    # 中圈
    circle = plt.Circle((60, 40), 10, color='black', fill=False, linewidth=2)
    ax.add_artist(circle)
    # 禁区（简化）
    ax.plot([0, 18], [18, 18], 'black')
    ax.plot([18, 18], [18, 62], 'black')
    ax.plot([18, 0], [62, 62], 'black')
    ax.plot([120, 102], [18, 18], 'black')
    ax.plot([102, 102], [18, 62], 'black')
    ax.plot([102, 120], [62, 62], 'black')


fig, ax = plt.subplots(figsize=(14, 10))


positions = {}
for player in top_players:
    x = player_positions.loc[player, 'avg_x']
    y = 80 - player_positions.loc[player, 'avg_y']  # 翻转 y 轴
    positions[player] = (x, y)


for passer in top_players:
    for receiver in top_players:
        count = pass_m.loc[passer, receiver]
        if count > 0:
            x1, y1 = positions[passer]
            x2, y2 = positions[receiver]
            
            linewidth = max(0.5, count / pass_m.values.max() * 5)
            alpha = min(1.0, count / pass_m.values.max() + 0.2)
            ax.plot([x1, x2], [y1, y2], 'gray', linewidth=linewidth, alpha=alpha)


player_total_passes = pass_m.sum(axis=1)
sizes = player_total_passes / player_total_passes.max() * 500 + 50

for player in top_players:
    x, y = positions[player]
    ax.scatter(x, y, s=sizes[player], color='steelblue', edgecolors='black', linewidth=1.5, zorder=5)
   
    short_name = player.split()[-1]  
    ax.annotate(short_name, (x, y), textcoords="offset points", xytext=(0, 12),
                ha='center', fontsize=9, fontweight='bold')

ax.set_xlim(0, 120)
ax.set_ylim(0, 80)
ax.set_aspect('equal')
ax.set_title(f'Argentina Passing Network (Semi-final vs Croatia)', fontsize=14)
ax.set_xlabel('Attacking direction →')
ax.axis('off')  
draw_pitch(ax)
plt.tight_layout()
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'charts')
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(r"C:\Users\李小鹏\Desktop\python脚本\项目", 'passing_network.png'), dpi=150, bbox_inches='tight')
plt.show()
match_passes = df_clean[(df_clean['match_id'] == match_id) & 
                        (df_clean['type'] == 'Pass') & 
                        (df_clean['team'] == 'Argentina')].copy()

match_passes = match_passes.dropna(subset=['location_x', 'location_y', 'pass_end_x', 'pass_end_y'])

print(f"符合条件的传球数: {len(match_passes)}")
fig, ax = plt.subplots(figsize=(14, 10))

# 画球场边框（可选，这里简化为矩形）
ax.plot([0, 0], [0, 80], 'black', linewidth=1)
ax.plot([0, 120], [80, 80], 'black', linewidth=1)
ax.plot([120, 120], [80, 0], 'black', linewidth=1)
ax.plot([120, 0], [0, 0], 'black', linewidth=1)
# 中线
ax.plot([60, 60], [0, 80], 'black', linewidth=1, linestyle='--')

# 遍历每条传球，画线
for _, row in match_passes.iterrows():
    x1 = row['location_x']
    y1 = 80 - row['location_y']   # 翻转 y 轴，让图的上方是进攻方向
    x2 = row['pass_end_x']
    y2 = 80 - row['pass_end_y']
    # 用低透明度、细线，颜色代表是否成功（成功=蓝，失败=红）
    if row.get('pass_outcome') == 'Incomplete' or row.get('pass_outcome') == 'Pass Offside':
        color = 'red'
        alpha = 0.3
    else:
        color = 'steelblue'
        alpha = 0.15  # 成功传球更多，alpha设低一些
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=0.8, alpha=alpha)

ax.set_xlim(0, 120)
ax.set_ylim(0, 80)
ax.set_aspect('equal')
ax.set_title(f'Argentina Pass Map vs Croatia (Semi-final) - {len(match_passes)} passes')
ax.axis('off')

plt.tight_layout()
plt.savefig(os.path.join(r"C:\Users\李小鹏\Desktop\python脚本\项目", 'pass_network_raw2.png'), dpi=150, bbox_inches='tight')
plt.show()
semi_final_pass=player_stats[player_stats['match_id']==match_id][['player','passes','passes_completed','pass_accuracy']].sort_values(['passes', 'passes_completed'], ascending=[False, False])
print(semi_final_pass)
semi_final_dirrble=player_stats[player_stats['match_id']==match_id][['player','dribbles','dribbles_completed']].sort_values('dribbles_completed', ascending= False)
print(semi_final_dirrble)
# 提取阿根廷所有射门
shots_argentina = df_clean[(df_clean['team'] == 'Argentina')&(df_clean['match_id']==match_id)& (df_clean['type'] == 'Shot')].copy()

# 检查是否有坐标缺失
shots_argentina = shots_argentina.dropna(subset=['location_x', 'location_y'])


# 定义颜色映射
def shot_color(row):
    if row['shot_outcome'] == 'Goal':
        return 'green'
    elif row['shot_outcome'] in ['Saved', 'Saved Off Line']:
        return 'blue'
    else:
        return 'red'

colors = shots_argentina.apply(shot_color, axis=1)

# 点大小：与 xG 成正比，最小为 20，最大为 300
xg = shots_argentina['shot_xg'].fillna(0.05)
sizes = 20 + (xg / xg.max()) * 280

fig, ax = plt.subplots(figsize=(14, 10))

# 画简易球场
ax.plot([0, 0], [0, 80], 'black', linewidth=1.5)
ax.plot([0, 120], [80, 80], 'black', linewidth=1.5)
ax.plot([120, 120], [80, 0], 'black', linewidth=1.5)
ax.plot([120, 0], [0, 0], 'black', linewidth=1.5)
ax.plot([60, 60], [0, 80], 'black', linewidth=1.5, linestyle='--')
# 两个禁区（简化）
ax.plot([0, 18], [18, 18], 'black', linewidth=1)
ax.plot([18, 18], [18, 62], 'black', linewidth=1)
ax.plot([18, 0], [62, 62], 'black', linewidth=1)
ax.plot([120, 102], [18, 18], 'black', linewidth=1)
ax.plot([102, 102], [18, 62], 'black', linewidth=1)
ax.plot([102, 120], [62, 62], 'black', linewidth=1)

# 画射门点
ax.scatter(shots_argentina['location_x'], 
           80 - shots_argentina['location_y'],  # 翻转 y 轴，让进攻方向向上
           c=colors, s=sizes, alpha=0.7, edgecolors='black', linewidth=0.5)

# 标注进球（例如用星号或文字）
goals = shots_argentina[shots_argentina['shot_outcome'] == 'Goal']
for _, goal in goals.iterrows():
    ax.text(goal['location_x'], 80 - goal['location_y'], '★', 
            fontsize=14, color='gold', ha='center', va='center')

ax.set_xlim(0, 120)
ax.set_ylim(0, 80)
ax.set_aspect('equal')
ax.set_title('Argentina - All Shots (7 matches)', fontsize=14)
ax.axis('off')

# 图例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='green', label='Goal'),
    Patch(facecolor='blue', label='On target saved'),
    Patch(facecolor='red', label='Off target / Blocked')
]
ax.legend(handles=legend_elements, loc='lower left')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'shot_map_all.png'), dpi=150, bbox_inches='tight')
plt.show()
# 所有比赛的总数据（7场）
player_total = player_stats.groupby('player').sum(numeric_only=True).reset_index()
# 补上一些比率指标（如果需要）
player_total['pass_accuracy'] = player_total['passes_completed'] / player_total['passes'] * 100
player_total['dribble_success_rate'] = player_total['dribbles_completed'] / player_total['dribbles'] * 100
player_total.fillna(0, inplace=True)
metrics = ['shots', 'passes', 'pass_accuracy', 'dribbles_completed', 'tackles','interceptions', 'clearances', 'ball_recoveries']
min_passes = 10
player_filtered = player_total[player_total['passes'] >= min_passes].copy()

# 创建输出文件夹
radar_dir = os.path.join(output_dir, 'radar_individual')
os.makedirs(radar_dir, exist_ok=True)

# 计算每个指标的最大值（用于归一化）
max_vals = player_filtered[metrics].max()

for _, row in player_filtered.iterrows():
    player_name = row['player']
    # 提取指标值并归一化到 0-1
    values = row[metrics].values.astype(float)
    normalized = values / max_vals.values
    normalized = np.clip(normalized, 0, 1)  # 防止极端值
    
    # 雷达图设置
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    values_plot = normalized.tolist()
    values_plot += values_plot[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values_plot, alpha=0.25, color='steelblue')
    ax.plot(angles, values_plot, color='steelblue', linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    ax.set_title(player_name, fontsize=14, pad=20)
    
    # 保存图片，文件名用球员名（替换特殊字符）
    safe_name = player_name.replace(' ', '_').replace('/', '_')
    plt.tight_layout()
    plt.savefig(os.path.join(radar_dir, f'{safe_name}.png'), dpi=150)
    plt.close(fig)  

print(f"已生成 {len(player_filtered)} 张球员雷达图，保存在 {radar_dir}")
