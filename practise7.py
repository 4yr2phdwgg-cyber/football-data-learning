import pandas as pd
dat={
    "球队":["皇马","拜仁","曼联","切尔西","利物浦"],
    "进球":[40,45,43,34,35],
    "失球":[20,23,12,15,19]
}
df=pd.DataFrame(dat)
df['净胜球']=df['进球']-df['失球']
max_goal=df['进球'].max()
max_team=df.loc[df['进球'].idxmax(),'球队']
max_own_goal=df['净胜球'].max()
best_team=df.loc[df['净胜球'].idxmax(),'球队']
average_goal=df['进球'].mean()
average_own_goal=df['净胜球'].mean()
print(df.head(3))
print(f"进球最多的球队是{max_team}，进了{max_goal}个，净胜球最多的球队是{best_team}，共有个{max_own_goal}")
print(f"平均进球数：{average_goal}，平均净胜球数：{average_own_goal}")


