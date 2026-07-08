#name=input("请输入球员姓名")
#goals=input("请输入球员进球数")
#assists=input("请输入球员助攻数")
#matches=input("请输入球员比赛场数")
import1=input("请输入球员姓名，进球数，助攻数，比赛场次。每个数据中间用逗号隔开")
parts=import1.strip().split(",")
player={"name":parts[0],"goals":int(parts[1]),"assists":int(parts[2]),"matches":int(parts[3])}
contribution=(player["goals"]+player["assists"])/player["matches"]
def player_judge(cont):
    if cont>0.8:
        return "超级核心"
    elif cont>0.5:
        return "主力轮换"
    else:
        return "替补"
player_rank=player_judge(contribution)
print(f"{player['name']}属于{player_rank}")