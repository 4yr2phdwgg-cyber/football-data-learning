import pandas as pd

data = {
    "球队": ["皇马","曼城","拜仁","利物浦","皇马","曼城","拜仁"],
    "赛季": ["2023","2023","2023","2023","2024","2024","2024"],
    "进球": [45, 52, 38, 41, 50, 48, 42],
    "失球": [25, 30, 22, 28, 27, 29, 24],
    "胜场": [18, 20, 15, 16, 22, 19, 17]
}

df = pd.DataFrame(data)

# 练习任务：
# 1. 按球队统计总进球和平均胜场
# 2. 按赛季统计平均进球
# 3. 找出每个赛季进球最多的球队
# 4. 计算每支球队的净胜球总和（进球-失球）

# 请你独立完成以上4个统计，并打印清晰结果
grouped1=df.groupby("球队")
result1=grouped1.agg(
    总进球=("进球","sum"),
    平均胜场=("胜场","mean")
)
print(result1)
grouped2=df.groupby(["赛季"])
result2=grouped2.agg(平均进球=("进球","mean"))
print(result2)
grouped3=df.groupby("赛季")
result3=df.loc[grouped3["进球"].idxmax()]
print(result3[["赛季","球队","进球"]])
df['净胜球']=df['进球']-df['失球']
grouped4=df.groupby("球队")
result4=grouped4.agg(平均净胜球=("净胜球","mean"))
print(result4)