
import os
def player_add(player,filename):
    with open(filename,"w",encoding="utf-8")as f:
        line=f"{player['name']},{player['goals']},{player['assists']},{player['matches']}\n"
        f.write(line)

if __name__=="__main__":
    information=input("请输入球员信息，进球，助攻，比赛场次")
    parts=information.strip().split(",")
    if len(parts) !=4:
        print("输入格式有误，请检查格式")
    else:
        
           player={
                  "name":parts[0].strip(),
                  "goals":int(parts[1].strip()),
                  "assists":int(parts[2].strip()),
                  "matches":int(parts[3].strip())
                  } 
           print(player)
    output_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"players.txt")
    player_add(player,output_path)
    print("添加完成")