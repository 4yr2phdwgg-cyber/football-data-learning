import os
import pandas as pd

script_dir=os.path.dirname(os.path.abspath(__file__))
csv_path=os.path.join(script_dir,"players.csv")

df=pd.read_csv(csv_path)

def judge_player(row):
    pos = row["position"]
    
    if pos in ("ST", "LW", "RW"):
        return (row["sg"] * 0.25 + row["sa"] * 0.1 + row["s_g/s"] * 0.15 +
                row["sip"] * 0.1 + row["ssb"] * 0.1 + row["ssa"] * 0.1 +
                row["so"] * 0.05 + row["sf"] * 0.05 + row["sm"] * 0.05)
    
    elif pos in ("CM", "AM", "DM"):
        return (row["ssp"] * 0.1 + row["sdp"] * 0.15 + (row["sg"] + row["sa"]) * 0.18 +
                row["ssd"] * 1.0 + (row["sbr"] + row["sob"]) * 0.15 + row["ssa"] * 0.1 +
                row["sbb"] * 0.05 + row["slm"] * 0.05 + row["sf"] * 0.05 + row["sm"] * 0.07)
    
    elif pos in ("CB", "FB", "WB"):
        return ((row["sbr"] + row["sob"]) * 0.16 + (row["s_j"] + row["s_f"]) * 0.08 +
                row["ssh"] * 0.15 + row["ssag"] * 0.8 + row["ssp"] * 0.1 + row["slp"] * 0.05 +
                (row["sa"] + row["sip"]) * 0.1 + row["sbb"] * 0.08 + row["slm"] * 0.1 +
                row["sf"] * 0.05 + row["sm"] * 0.05)
    
    elif pos == "GK":
        return (row["sk"] * 0.25 + row["ssbrr"] * 0.15 + row["sz"] * 0.1 + row["ssp"] * 0.12 +
                row["slp"] * 0.08 + row["ssg"] * 0.5 + row["slm"] * 0.15 + row["sf"] * 0.05 +
                row["sm"] * 0.05)
    
    else:
        return None   
    
df["score"]=df.apply(judge_player,axis=1)
good_judge=df["score"].mean()
good_players=df.loc[df['score']>=good_judge]
print(good_players[['name','score','position']])
rank=df.sort_values("score",ascending=False)
rank['nu']=range(1,len(rank)+1)
print(rank[['nu','name','score']])
imp_score=df['score'].quantile(0.8)
aimp_score=df['score'].quantile(0.3)
#df1=df.loc[df['score']>=imp_score]
#df2=df.loc[df['score']<=aimp_score]
#df3=df.loc[(df['score']<imp_score)&(df['score']>aimp_score)]
#df1['status']="核心"
#df2['status']="边缘"
#df3['status']="常规"
#all_df=pd.concat([df1,df2,df3],ignore_index=True)
#rank_all=all_df.sort_values("score",ascending=False)
#print(rank_all[['name','score','status']])
rank['status']="null"
rank.loc[rank['score']>=imp_score,'status']="核心"
rank.loc[rank['score']<=aimp_score,'status']="边缘"
rank.loc[rank['status']=="null",'status']="常规"
print(rank[['nu','name','score','status']])
imp=len(rank.loc[rank['status']=="核心"])
aimp=len(rank.loc[rank['status']=="边缘"])
elsebody=len(rank.loc[rank['status']=="常规"])
print(f"核心有{imp}人，常规有{elsebody}人，边缘有{aimp}人")
rank_small1=rank.iloc[:5,:4]
print(rank_small1)
rank_small2=rank.iloc[-2:,-3:]
print(rank_small2)
for i, col in enumerate(rank.columns):
        print(f"位置 {i}: {col}")
print(rank.iloc[0:3])

import numpy as np
df_miss=rank.copy()
df_miss.loc[2,'sg']=np.nan
df_miss.loc[4,'sa']=np.nan
df_miss.loc[0,'score']=np.nan
print(f"缺失值统计{df_miss.isnull().sum()}")
df_goal=df_miss.dropna(subset=['score'])
print(f"前行数{len(df_miss)},后行数{len(df_goal)}")
df_v=df_miss.dropna(subset=['sg','sa'])
print(f"删除后行数{len(df_v)}")
df_fill=df_miss.copy()
df_fill['sg']=df_fill['sg'].fillna(0)
df_fill['sa']=df_fill['sa'].fillna(0)
df_fill['score']=df_fill['score'].fillna(df_fill['score'].mean())
print("填充前")
print(df_miss.agg({
     "score":['mean','max','min'],
     "sg":['mean','max','min'],
     "sa":['mean','max','min']
}))
print("填充后")
print(df_fill.agg({
     "score":['mean','max','min'],
     "sg":['mean','max','min'],
     "sa":['mean','max','min']
}))

df_com=pd.DataFrame({"name":[],
        "bscore":[],
        "ascore":[]})
df_com['name']=df_fill['name']
df_com['bscore']=df_miss['score']
df_com['ascore']=df_fill.apply(judge_player,axis=1)
print(df_com)