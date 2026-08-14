import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ===================== 数据获取函数 =====================
def find_competition(root, com_name, season_name):
    filepath = os.path.join(root, "competitions.json")
    with open(filepath, "r", encoding="utf-8") as f:
        com = json.load(f)
    for item in com:
        if item["competition_name"] == com_name and item["season_name"] == season_name:
            return item["competition_id"], item["season_id"]
    raise ValueError(f"未找到 {com_name} {season_name} 赛季的数据")


def find_matchids(root, com_id, sea_id, team):
    filepath = os.path.join(root, "matches", str(com_id), f"{sea_id}.json")
    with open(filepath, "r", encoding="utf-8") as f:
        match = json.load(f)
    mat_ids = []
    match_sc = []
    for item in match:
        home = item["home_team"]["home_team_name"]
        away = item["away_team"]["away_team_name"]
        if home == team or away == team:
            mid = item["match_id"]
            mat_ids.append(mid)
            match_sc.append({
                "match_id": mid,
                "home": home,
                "away": away,
                "score": f"{item['home_score']}:{item['away_score']}",
                "stage": item["competition_stage"]["name"]
            })
    return mat_ids, pd.DataFrame(match_sc)


def events_load(root, mid):
    filepath = os.path.join(root, "events", f"{mid}.json")
    with open(filepath, "r", encoding="utf-8") as f:
        event = json.load(f)
    return event


# ===================== 数据处理函数 =====================
def parse_events_to_df(events_list, match_id):
    rows = []
    for ev in events_list:
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
        shot_info = ev.get('shot', {})
        if shot_info:
            row['shot_outcome'] = shot_info.get('outcome', {}).get('name')
            row['shot_xg'] = shot_info.get('statsbomb_xg')
            row['shot_body_part'] = shot_info.get('body_part', {}).get('name')
            row['shot_technique'] = shot_info.get('technique', {}).get('name')
        dribble_info = ev.get('dribble', {})
        if dribble_info:
            row['dribble_outcome'] = dribble_info.get('outcome', {}).get('name')
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
        foul_committed = ev.get('foul_committed', {})
        if foul_committed:
            row['foul_type'] = foul_committed.get('type', {}).get('name')
            row['card'] = foul_committed.get('card', {}).get('name')
        rows.append(row)
    return pd.DataFrame(rows)


def load_all_events(root, match_ids):
    all_dfs = []
    for mid in match_ids:
        events_list = events_load(root, mid)
        df = parse_events_to_df(events_list, mid)
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)


def wash(df):
    action_types = ['Pass', 'Shot', 'Dribble', 'Ball Recovery', 'Duel',
                    'Clearance', 'Interception', 'Block', 'Foul Committed',
                    'Pressure', '50/50', 'Offside', 'Bad Behaviour']
    return df[df['type'].isin(action_types)].copy()


def team_stats(df):
    passes = df[df['type'] == 'Pass']
    total_passes = len(passes)
    passes_completed = passes[passes['pass_outcome'].isna() |
                              passes['pass_outcome'].str.contains('Complete', na=False)].shape[0]
    shots = df[df['type'] == 'Shot']
    total_shots = len(shots)
    shot_on_target = shots['shot_outcome'].isin(['Saved', 'Goal']).sum()
    goals = (shots['shot_outcome'] == 'Goal').sum()
    xg_total = shots['shot_xg'].sum()
    dribbles = df[df['type'] == 'Dribble']
    total_dribbles = len(dribbles)
    dribbles_completed = (dribbles['dribble_outcome'] == 'Complete').sum()
    ball_recoveries = len(df[df['type'] == 'Ball Recovery'])
    duels = df[df['type'] == 'Duel']
    tackles = duels[duels['duel_type'] == 'Tackle']
    total_tackles = len(tackles)
    interceptions = len(df[df['type'] == 'Interception'])
    clearances = len(df[df['type'] == 'Clearance'])
    fouls = df[df['type'] == 'Foul Committed']
    total_fouls = len(fouls)
    yellows = (fouls['card'] == 'Yellow Card').sum()
    reds = (fouls['card'] == 'Red Card').sum()

    stats = {
        "passes": total_passes,
        "passes_completed": passes_completed,
        "pass_accuracy": passes_completed / total_passes * 100 if total_passes else 0,
        "shots": total_shots,
        "shot_on_target": shot_on_target,
        "goals": goals,
        "xg": xg_total,                     # 统一为小写
        "dribbles": total_dribbles,
        "dribbles_completed": dribbles_completed,
        "ball_recoveries": ball_recoveries,
        "duel_successful": total_tackles / len(duels) if len(duels) else 0,
        "tackles": total_tackles,
        "interceptions": interceptions,
        "clearances": clearances,
        "fouls": total_fouls,
        "yellows": yellows,
        "reds": reds
    }
    return pd.Series(stats)


def player_stats(df):   # 注意：函数名与返回的变量名一样，不影响运行
    passes = df[df['type'] == 'Pass']
    total_passes = len(passes)
    passes_completed = passes[passes['pass_outcome'].isna() |
                              passes['pass_outcome'].str.contains('Complete', na=False)].shape[0]
    shots = df[df['type'] == 'Shot']
    total_shots = len(shots)
    shot_on_target = shots['shot_outcome'].isin(['Saved', 'Goal']).sum()
    goals = (shots['shot_outcome'] == 'Goal').sum()
    xg_total = shots['shot_xg'].sum()
    dribbles = df[df['type'] == 'Dribble']
    total_dribbles = len(dribbles)
    dribbles_completed = (dribbles['dribble_outcome'] == 'Complete').sum()
    ball_recoveries = len(df[df['type'] == 'Ball Recovery'])
    duels = df[df['type'] == 'Duel']
    tackles = duels[duels['duel_type'] == 'Tackle']
    total_tackles = len(tackles)
    interceptions = len(df[df['type'] == 'Interception'])
    clearances = len(df[df['type'] == 'Clearance'])
    fouls = df[df['type'] == 'Foul Committed']
    total_fouls = len(fouls)
    yellows = (fouls['card'] == 'Yellow Card').sum()
    reds = (fouls['card'] == 'Red Card').sum()
    passes_received = len(df[df['pass_recipient'].notna()])

    stats = {
        "passes": total_passes,
        "passes_completed": passes_completed,
        "pass_accuracy": passes_completed / total_passes * 100 if total_passes else 0,
        "shots": total_shots,
        "shot_on_target": shot_on_target,
        "goals": goals,
        "xg": xg_total,                     # 统一为小写
        "dribbles": total_dribbles,
        "dribbles_completed": dribbles_completed,
        "ball_recoveries": ball_recoveries,
        "duel_successful": total_tackles / len(duels) if len(duels) else 0,
        "tackles": total_tackles,
        "interceptions": interceptions,
        "clearances": clearances,
        "fouls": total_fouls,
        "yellows": yellows,
        "reds": reds,
        "passes_received": passes_received,
    }
    return pd.Series(stats)


# ===================== 可视化辅助函数 =====================
def draw_pitch(ax):
    ax.plot([0, 0], [0, 80], 'black', linewidth=2)
    ax.plot([0, 120], [80, 80], 'black', linewidth=2)
    ax.plot([120, 120], [80, 0], 'black', linewidth=2)
    ax.plot([120, 0], [0, 0], 'black', linewidth=2)
    ax.plot([60, 60], [0, 80], 'black', linewidth=2)
    circle = plt.Circle((60, 40), 10, color='black', fill=False, linewidth=2)
    ax.add_artist(circle)
    ax.plot([0, 18], [18, 18], 'black')
    ax.plot([18, 18], [18, 62], 'black')
    ax.plot([18, 0], [62, 62], 'black')
    ax.plot([120, 102], [18, 18], 'black')
    ax.plot([102, 102], [18, 62], 'black')
    ax.plot([102, 120], [62, 62], 'black')


def pass_formation(df, mid, output_dir, team):
    passes = df[(df['match_id'] == mid) & (df['team'] == team) & (df['type'] == 'Pass')].copy()
    passes = passes.dropna(subset=['player', 'pass_recipient'])
    print(f"有效传球数: {len(passes)}")
    passes_count = passes.groupby(['player', 'pass_recipient']).size().reset_index(name="counts")
    # 保存 CSV 到输出目录，带比赛 ID
    csv_path = os.path.join(output_dir, f"passes_count_{mid}.csv")
    passes_count.to_csv(csv_path, index=False, encoding="utf-8")
    pass_m = passes_count.pivot(index='player', columns='pass_recipient', values='counts').fillna(0)
    top_players = passes['player'].value_counts().head(11).index.tolist()
    pass_m = pass_m.reindex(index=top_players, columns=top_players, fill_value=0)
    player_positions = passes.groupby('player').agg(
        avg_x=('location_x', 'mean'),
        avg_y=('location_y', 'mean')
    ).reindex(top_players)
    return player_positions, top_players, pass_m


def draw_position(top_players, player_positions, pass_m, output_path):
    fig, ax = plt.subplots(figsize=(14, 10))
    positions = {player: (player_positions.loc[player, 'avg_x'],
                          80 - player_positions.loc[player, 'avg_y'])
                 for player in top_players}
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
    ax.set_title('Passing Network', fontsize=14)
    ax.axis('off')
    draw_pitch(ax)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_raw_pass_map(df_clean, match_id, team_name, output_path):
    match_passes = df_clean[(df_clean['match_id'] == match_id) &
                            (df_clean['type'] == 'Pass') &
                            (df_clean['team'] == team_name)].copy()
    match_passes = match_passes.dropna(subset=['location_x', 'location_y', 'pass_end_x', 'pass_end_y'])
    print(f"符合条件的传球数: {len(match_passes)}")
    fig, ax = plt.subplots(figsize=(14, 10))
    draw_pitch(ax)
    for _, row in match_passes.iterrows():
        x1 = row['location_x']
        y1 = 80 - row['location_y']
        x2 = row['pass_end_x']
        y2 = 80 - row['pass_end_y']
        if row.get('pass_outcome') in ['Incomplete', 'Pass Offside']:
            color, alpha = 'red', 0.3
        else:
            color, alpha = 'steelblue', 0.15
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=0.8, alpha=alpha)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.set_aspect('equal')
    ax.set_title(f'{team_name} Pass Map (Match {match_id}) - {len(match_passes)} passes')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_shot_map(df_clean, match_id, team_name, output_path):
    shots = df_clean[(df_clean['team'] == team_name) &
                     (df_clean['match_id'] == match_id) &
                     (df_clean['type'] == 'Shot')].copy()
    shots = shots.dropna(subset=['location_x', 'location_y'])
    def shot_color(row):
        if row['shot_outcome'] == 'Goal': return 'green'
        elif row['shot_outcome'] in ['Saved', 'Saved Off Line']: return 'blue'
        else: return 'red'
    colors = shots.apply(shot_color, axis=1)
    xg = shots['shot_xg'].fillna(0.05)
    sizes = 20 + (xg / xg.max()) * 280
    fig, ax = plt.subplots(figsize=(14, 10))
    draw_pitch(ax)
    ax.scatter(shots['location_x'], 80 - shots['location_y'],
               c=colors, s=sizes, alpha=0.7, edgecolors='black', linewidth=0.5)
    goals = shots[shots['shot_outcome'] == 'Goal']
    for _, goal in goals.iterrows():
        ax.text(goal['location_x'], 80 - goal['location_y'], '★',
                fontsize=14, color='gold', ha='center', va='center')
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.set_aspect('equal')
    ax.set_title(f'{team_name} Shot Map (Match {match_id})', fontsize=14)
    ax.axis('off')
    legend_elements = [
        Patch(facecolor='green', label='Goal'),
        Patch(facecolor='blue', label='On target saved'),
        Patch(facecolor='red', label='Off target / Blocked')
    ]
    ax.legend(handles=legend_elements, loc='lower left')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_individual_radars(player_stats_df, output_dir, metrics=None, min_passes=10):
    if metrics is None:
        metrics = ['shots', 'passes', 'pass_accuracy', 'dribbles_completed',
                   'tackles', 'interceptions', 'clearances', 'ball_recoveries']
    player_total = player_stats_df.groupby('player').sum(numeric_only=True).reset_index()
    player_total['pass_accuracy'] = (player_total['passes_completed'] / player_total['passes'] * 100).fillna(0)
    player_total['dribble_success_rate'] = (player_total['dribbles_completed'] / player_total['dribbles'] * 100).fillna(0)
    player_total.fillna(0, inplace=True)
    player_filtered = player_total[player_total['passes'] >= min_passes].copy()
    os.makedirs(output_dir, exist_ok=True)
    max_vals = player_filtered[metrics].max()
    for _, row in player_filtered.iterrows():
        player_name = row['player']
        values = row[metrics].values.astype(float)
        normalized = np.clip(values / max_vals.values, 0, 1)
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        values_plot = normalized.tolist() + normalized.tolist()[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, values_plot, alpha=0.25, color='steelblue')
        ax.plot(angles, values_plot, color='steelblue', linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics, fontsize=8)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        ax.set_title(player_name, fontsize=14, pad=20)
        safe_name = player_name.replace(' ', '_').replace('/', '_')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{safe_name}.png'), dpi=150)
        plt.close(fig)
    print(f"已生成 {len(player_filtered)} 张球员雷达图，保存在 {output_dir}")


# ===================== 主程序 =====================
def main():
    ROOT = r"C:\Users\李小鹏\Desktop\python脚本\项目\open-data-master\data"
    COMPETITION = "FIFA World Cup"
    SEASON = "2022"
    TEAM = "Argentina"
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("步骤1：查找赛事信息...")
    try:
        com_id, sea_id = find_competition(ROOT, COMPETITION, SEASON)
        print(f"✅ 赛事ID: {com_id}, 赛季ID: {sea_id}")
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("\n步骤2：获取比赛列表...")
    match_ids, match_df = find_matchids(ROOT, com_id, sea_id, TEAM)
    print(f"✅ 共找到 {len(match_ids)} 场比赛：")
    print(match_df[['match_id', 'stage', 'home', 'away', 'score']].to_string(index=False))

    print("\n步骤3：加载事件数据...")
    df_all = load_all_events(ROOT, match_ids)
    print(f"✅ 总事件数: {len(df_all)}")

    print("\n步骤4：清洗数据...")
    df_clean = wash(df_all)
    print(f"✅ 清洗后事件数: {len(df_clean)}")

    print("\n步骤5：计算团队统计数据...")
    team_result = df_clean.groupby(['match_id', 'team']).apply(team_stats).reset_index()
    team_result.to_csv(os.path.join(OUTPUT_DIR, 'team_stats.csv'), index=False, encoding='utf-8')
    print("✅ 团队统计已保存")

    print("\n步骤6：计算球员统计数据...")
    team_events = df_clean[df_clean['team'] == TEAM].copy()
    player_result = team_events.groupby(['match_id', 'player']).apply(player_stats).reset_index()
    player_result.to_csv(os.path.join(OUTPUT_DIR, 'player_stats.csv'), index=False, encoding='utf-8')
    print("✅ 球员统计已保存")

    print("\n步骤7：生成可视化图表...")
    for mid in match_ids:
        stage = match_df[match_df['match_id'] == mid]['stage'].values[0]
        print(f"  处理比赛 {mid} ({stage})...")

        # 1. 传球网络图
        try:
            positions, top_players, pass_matrix = pass_formation(df_clean, mid, OUTPUT_DIR, TEAM)
            if len(top_players) >= 2:
                net_path = os.path.join(OUTPUT_DIR, f'passing_network_{mid}.png')
                draw_position(top_players, positions, pass_matrix, net_path)
            else:
                print("    ⚠️ 传球数据不足，跳过网络图")
        except Exception as e:
            print(f"    ⚠️ 传球网络图失败: {e}")

        # 2. 原始传球线路图
        try:
            raw_path = os.path.join(OUTPUT_DIR, f'raw_passes_{mid}.png')
            plot_raw_pass_map(df_clean, mid, TEAM, raw_path)
        except Exception as e:
            print(f"    ⚠️ 原始传球图失败: {e}")

        # 3. 射门地图
        try:
            shot_path = os.path.join(OUTPUT_DIR, f'shot_map_{mid}.png')
            plot_shot_map(df_clean, mid, TEAM, shot_path)
        except Exception as e:
            print(f"    ⚠️ 射门地图失败: {e}")

    # 4. 球员雷达图
    print("\n  生成球员雷达图...")
    try:
        radar_dir = os.path.join(OUTPUT_DIR, 'radar_individual')
        plot_individual_radars(player_result, radar_dir)
    except Exception as e:
        print(f"    ⚠️ 雷达图失败: {e}")

    print("\n" + "=" * 50)
    print("📊 分析报告摘要")
    argentina_stats = team_result[team_result['team'] == TEAM]
    print(f"总进球: {argentina_stats['goals'].sum()}")
    print(f"总射门: {argentina_stats['shots'].sum()}")
    print(f"平均传球成功率: {argentina_stats['pass_accuracy'].mean():.1f}%")
    print(f"总 xG: {argentina_stats['xg'].sum():.2f}")
    print(f"\n所有文件已保存到: {OUTPUT_DIR}")
    print("✅ 分析完成！")


if __name__ == "__main__":
    main()