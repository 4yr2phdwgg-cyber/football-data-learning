import os

def add_player(filename):
    """添加新球员"""
    input_str = input("请输入球员信息（姓名,进球,助攻,比赛场数），用逗号隔开：")
    parts = input_str.strip().split(",")
    
    if len(parts) != 4:
        print("输入格式错误！请按要求输入4个数据（用逗号隔开）")
        return
    
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"{parts[0].strip()},{int(parts[1])},{int(parts[2])},{int(parts[3])}\n")
        print("✅ 球员添加成功！")
    except ValueError:
        print("输入格式错误！进球、助攻、场数必须是数字")


def show_all_players(filename):
    """显示所有球员"""
    print("\n--- 所有球员信息 ---")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            next(f)  # 跳过标题行
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 4:
                    print(f"球员：{parts[0]}, 进球：{parts[1]}, 助攻：{parts[2]}, 比赛场数：{parts[3]}")
                else:
                    print("数据格式异常，跳过该行")
    except FileNotFoundError:
        print("暂无球员数据，请先添加球员。")


def team_stats(filename):
    """球队数据统计"""
    total_goals = 0
    player_count = 0
    top_players = []
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            next(f)  # 跳过标题
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 3:
                    goals = int(parts[1])
                    assists = int(parts[2])
                    total_goals += goals
                    player_count += 1
                    
                    if goals + assists >= 20:
                        top_players.append(parts[0])
        
        if player_count == 0:
            print("暂无球员数据")
            return
        
        average_goals = total_goals / player_count
        
        print("\n--- 球队数据统计 ---")
        print(f"全队总进球：{total_goals}")
        print(f"全队平均进球：{average_goals:.1f}")
        if top_players:
            print(f"顶级球员共有 {len(top_players)} 位：{', '.join(top_players)}")
        else:
            print("暂无顶级球员（进球+助攻≥20）")
            
    except FileNotFoundError:
        print("暂无球员数据，请先添加球员。")


def main():
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players.txt")
    
    # 初始化文件
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("name,goals,assists,matches\n")
    
    while True:
        print("\n=== 足球球员管理系统 ===")
        print("1. 添加球员")
        print("2. 查看所有球员")
        print("3. 球队数据统计")
        print("4. 退出")
        
        choice = input("请选择功能（1-4）：")
        
        if choice == "1":
            add_player(filename)
        elif choice == "2":
            show_all_players(filename)
        elif choice == "3":
            team_stats(filename)
        elif choice == "4":
            print("再见！")
            break
        else:
            print("输入错误，请重新输入")


if __name__ == "__main__":
    main()