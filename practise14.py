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
midfielders = df[df['position'].isin(['CM', 'AM', 'DM'])]
mid_rank = midfielders.sort_values(['ssp', 'sdp'], ascending=[False, False])
print(mid_rank[['name', 'ssp', 'sdp']])
attacker = df[df['position'].isin(['LW', 'RW', 'ST'])]
attacker['attack_sum']=attacker['sg']+attacker['sa']+attacker['sip']
attacker['rank']=range(1,len(attacker.sort_values('attack_sum',ascending=False))+1)
print(attacker[['name','rank','position','sg','sa','sip','attack_sum']])
df_name=df.set_index('name')
df_name_sort=df_name.sort_index()
print(df_name_sort[['position','score']].head(3))
df_position=df.sort_values('score',ascending=False)
df_2=df_position.groupby('positon').head(1)
df_3=df_2.sort_values('score',ascending=False)
print(df_3[['name','position','score']])

