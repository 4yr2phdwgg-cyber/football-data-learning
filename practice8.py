import pandas as pd

df = pd.DataFrame({
    "球队": ["皇马","曼城","拜仁","利物浦","切尔西"],
    "进球": [45,52,38,41,35],
    "失球": [25,30,22,28,19],
    "胜场": [18,20,15,16,14]
})
# 使用上面示例数据
# 1. 筛选出进球数大于40的球队
# 2. 筛选出净胜球（进球-失球）大于15的球队
# 3. 打印这些球队的完整信息
# 计算：
# - 每支球队的平均进球
# - 总胜场最多的球队
# - 整体平均净胜球
df['净胜球']=df['进球']-df['失球']
attack_teams=df[df['进球']>40]
good_teams=df[df['净胜球']>15]
average_goals=df["进球"].mean()
best_team=df.loc[df['胜场'].idxmax(),'球队']
average_own_goals=df['净胜球'].mean()
print(f"进球数大于40的球队{attack_teams}")
print(f"净胜球大于15的球队{good_teams}")
print(f"胜场最多的球队{best_team}")
print(f"平均进球{average_goals}，平均净胜球{average_own_goals}")



    