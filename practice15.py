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
#用 pivot_table 计算每个位置的平均 score、最高 sg、平均 sa
#用 fill_value=0 处理空值
#添加 margins=True 看全队总计
#打印结果

df1=pd.pivot_table(df,values=['score','sa'],index='position',aggfunc='mean',margins=True,fill_value=0)
df2=pd.pivot_table(df,values='sg',index='position',aggfunc='max',margins=True,fill_value=0)
df3=pd.merge(df1,df2,on='position',how='outer')
print(df3)
#创建一个新列 role_group：把 ST/LW/RW 归为 '前锋'，CM/AM/DM 归为 '中场'，CB/FB/WB 归为 '后卫'，GK 归为 '门将'
#用 pivot_table 按 role_group 统计平均 score 和球员人数
#按平均分降序排列
df["role_group"]="null"
df.loc[df['position'].isin(['ST','LW','RW']),'role_group']="前锋"
df.loc[df['position'].isin(['AM','CM','DM']),'role_group']="中场"
df.loc[df['position'].isin(['CB','FB','WB']),'role_group']="后卫"
df.loc[df['position']=="GK",'role_group']="门将"
df4=pd.pivot_table(df,values='score',index='role_group',aggfunc=['mean','count'])
df4.columns=['ascore','count']
df5=df4.sort_values('ascore',ascending=False)
print(df5)
#给 df 添加一个 team 列，模拟 3 支不同球队（比如手动指定：前3人巴黎，中间2人皇马，后面巴萨，其余自由分配）
#用 pivot_table 制作：行=球队，列=位置，值=平均 score，fill_value=0
#打印这个二维交叉表
df["team"]="null"
df.loc[0:2,'team']="巴黎"
df.loc[3:4,'team']="皇马"
df.loc[5:,'team']="巴萨"
df6=pd.pivot_table(df,values='score',index='team',columns='position',aggfunc='mean',fill_value=0)
print(df6)
#对同一张透视表同时使用 mean 和 max（传入 aggfunc=['mean', 'max']）
#索引按球队，值按 score
#打印结果
df7=pd.pivot_table(df,values='score',index='team',aggfunc=['mean','max'])
print(df7)