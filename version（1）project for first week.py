def add_player(filename):
    input_str=input("请输入球员信息")
    parts=input_str.strip().split(",")
    if len(parts)!=4:
       print("输入格式有误，请重新输入")
       return
    try:
       with open(filename,"a",encoding="utf-8")as f:
          f.write(f"{parts[0].strip()},{int(parts[1])},{int(parts[2])},{int(parts[3])}\n")
    except:
       print("输入格式有误")

def show_all_players(filename):
    with open(filename,"r",encoding="utf-8")as f:
        next (f)
        for line in f:
            parts=line.strip().split(",")
            print(f"球员{parts[0]},进球{parts[1]},助攻{parts[2]},比赛场次{parts[3]}")
    


def teams_stats(filename):
    total_goals=0
    player_count=0
    top_players=[]
    with open(filename,"r",encoding="utf-8")as f:
        next(f)
        for line in f:
            parts=line.strip().split(",")
            if parts[1]+parts[2]>=20:
                top_players.append(parts[0])
            player_count+=1
            total_goals=total_goals+int(parts[1])
        average_goals=total_goals/player_count
        print(f"全队总进球:{total_goals}")
        print(f"全队平均进球：{average_goals}")
        if top_players!=[]:
           print(f"顶级球员有{top_players},顶级球员有{len(top_players)}人")
        else:
            print("没有顶级球员")

def main():
    filename="players.txt"
    while True:
        print("\n===球员管理系统===")
        print("1.球员添加")
        print("2.查看所有球员")
        print("3.球队数据统计")
        print("4.退出")
        
        choice=input("请输入1-4：")
        if choice=="1":
            add_player(filename)
        elif choice=="2":
            show_all_players(filename)
        elif choice=="3":
            teams_stats(filename)
        elif choice=="4":
            print("再见")
            break
        else:
            print("输入错误，重新输入")
if __name__=="__main__":
    main()
