#with open("player.txt","w",encoding="utf-8")as f:
    #f.write("messi,25\n")
    #f.write("jackson,21\n")
#with open ("player.txt","r",encoding="utf-8")as f:
    #content=f.read()
    #print(content)
#with open ("player.txt","r",encoding="utf-8")as f:
    #for line in f:
        #print(line.strip())
                                        
players=[
    "messi,25,10",
    "mbappe,22,8",
    "haaland,30,5"
]
with open("player.txt","w",encoding="utf-8")as f:
    f.write("name,goals,assists\n")
    for player in players:
        f.write(f"{player}\n")
with open("player.txt","r",encoding="utf-8")as f:
    content=f.read()
    print(content)
with open("player.txt","r",encoding="utf-8")as f:
    next(f)
    total_goal=0
    for line in f:
        parts=line.strip().split(",")
        total_goal=total_goal+int(parts[1])
    print(f"总进球数为{total_goal}")
        
        
