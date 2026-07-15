#任务 1：数据读取与合并（merge
#读取 players_main.csv 1和 match_log.csv2
#用 merge 把比赛日志合并到球员主表，按 player_id，使用左连接
#打印合并后的行数和列数
import os
import pandas as pd
filepath1=os.path.join(os.path.dirname(os.path.abspath(__file__)),"players1.csv")
filepath2=os.path.join(os.path.dirname(os.path.abspath(__file__)),"players2.csv")
df1=pd.read_csv(filepath1)
df2=pd.read_csv(filepath2)
df2_1=df2.groupby(['player_id'])
df2_2=df2_1.agg(
    match=("match","sum"),
    minutes=("minutes","sum"),
    shots=("shots","sum"),
    shots_on_target=("shots_on_target","sum"),
    key_passes=("key_passes","sum"),
    dribbles=("dribbles","sum"),
    duels_won=("duels_won","sum"),
    aerial_won=("aerial_won","sum"),
    clearances=("clearances","sum"),
    saves=("saves","sum"),
    penalties_saved=("penalties_saved","sum"),
)

df2_v=pd.DataFrame(df2_2)
print(df2_v)
merged=pd.merge(df1,df2_v,on='player_id',how='left')
print(f"行数{len(merged)},列数{len(merged.columns)}")
#任务 2：缺失值处理（fillna/dropna）
#检查合并后每列的缺失值数量
#对数值列（如 shots, key_passes 等）的缺失值用 该列中位数 填充
#如果存在任何 player_id 缺失的行，删除它们
#再次打印缺失值统计，确认没有 NaN
merged1=merged.dropna(subset='player_id')
merged1=merged.fillna(merged.mean(numeric_only=True))
print(sum(merged1.isnull().sum()))
#任务 3：精准定位与计算新列（loc）
#用 loc 和布尔条件，找出 position == 'GK' 的门将，将其 shots 和 goals 设为 0（因为门将一般不参与进攻统计）
#创建新列 scoring_efficiency（得分效率） = goals / shots，如果 shots 为 0 则填充 0
#创建新列 defensive_score（防守综合分） = interceptions + tackles - errors * 2
#用 loc 给 defensive_score 最高的 3 名球员标记 elite_defender = True，其余为 False
merged1.loc[merged1['position']=='GK',['shots','goals']]=0
print(merged1)
def judge_attack(row):
    if row['shots']==0:
        return 0
    else:
        return row['goals']/row['shots']
merged1['scoring_efficiency']=merged1.apply(judge_attack,axis=1)
merged1['defensive_score']=merged1['interceptions']+merged1['tackles']-merged1['errors']*2 
merged1['elite_defender']="False"
top3_idx = merged1.sort_values('defensive_score', ascending=False).head(3).index
merged1.loc[top3_idx, 'elite_defender'] = "True"
#任务 4：排序制作排行榜（sort_values）
#制作“进攻效率榜”：按 scoring_efficiency 降序排列，只显示非门将球员，取前 5 名
#制作“防守贡献榜”：按 defensive_score 降序排列，取前 5 名
#制作“球队场均数据榜”：按 team 分组，计算 shots 和 key_passes 的场均均值（数据来自比赛日志），然后按 shots 降序排列
b=merged1.loc[(merged1['position']!="GK").index]
top5_attack=b.sort_values('scoring_efficiency',ascending=False).head(5)
top5_defence=merged1.sort_values('defensive_score',ascending=False).head(5)
merged1['ashots']=merged1['shots']/merged1['match']
merged1['akeypasses']=merged1['key_passes']/merged1['match']
c=merged1.groupby('team')
result=c.agg(
    场均射门=("ashots","mean"),
    场均关键传球=("akeypasses","mean")
)
#任务 5：透视表综合报告（pivot_table）
#创建透视表：行 = team，列 = position，值 = scoring_efficiency 的平均值，fill_value=0，并添加 margins
#创建第二个透视表：行 = team，值 = defensive_score 和 pass_completion，聚合函数分别为 sum 和 mean
#将两个透视表用 merge 合并（按 team），打印最终的球探综合报告
pi1=pd.pivot_table(merged1,values='scoring_efficiency',index='team',columns='position',aggfunc='mean',margins=True,fill_value=0)
pi2=pd.pivot_table(merged1,values=['defensive_score','pass_completion'],index='team',aggfunc=['mean','sum'])
pi2.columns = ['_'.join(col).strip() for col in pi2.columns.values]
pi2 = pi2.reset_index()
pi=pd.merge(pi1,pi2,on='team',how='inner')
print(pi)