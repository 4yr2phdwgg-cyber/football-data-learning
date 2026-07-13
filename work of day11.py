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
rank=df.sort_values("score",ascending=False)
best_plyer=df.sort_values("score",ascending=False).head(1)
print(rank[["name","position","score"]])
print(best_plyer["name"])

df['player_id']=range(1,len(df)+1)
salaries_data = {
    'player_id': [1, 2, 4, 5, 6, 7],   
    'weekly_salary': [250000, 80000, 60000, 120000, 50000, 35000],
    'market_value': [85, 25, 35, 50, 10, 8]
}

salaries_df = pd.DataFrame(salaries_data)

print("薪资数据：")
print(salaries_df)


merged1=pd.merge(df,salaries_df,on='player_id',how='left')
print(merged1)
merged1=pd.merge(df,salaries_df,on='player_id',how='inner')
merged1['score_weekly_salary']=merged1['score'] /merged1['weekly_salary']
print(merged1[['player_id','name','score_weekly_salary']])
salary_judge=merged1['weekly_salary'].quantile(0.5)
score_judge=merged1['score'].quantile(0.3)
a1=merged1[(merged1['score']<=score_judge)&(merged1['score_weekly_salary']>=salary_judge)]
if len(a1)==0:
    print("没有高薪低能球员")
else:
    print(f"\n高薪低能球员有：{a1[['name','score']].to_string(index=False)}")



    