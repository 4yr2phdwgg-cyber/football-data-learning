#nums=[10,20,30,40,50]
#w=nums.pop(-1)
#nums.remove(40)
#nums.append(90)
#pop后跟要删除的元素下标，而remove这是具体的元素数值，且pop有返回值,append是增加元素
#nums[1]=99 #替换元素
#nums.sort()
#nums.reverse()
#print(nums)
#print(w)
#print(len(nums))#计算元素个数数


teams=["皇马","曼城","拜仁","利物浦","AC米兰"]
print(teams[2])
teams.append("阿森纳")
teams.remove("拜仁")#or teams.pop(3)
print(len(teams))

player={"name":"pp",
        "position":"前锋",
        "goals":15,
        "assist":8
        }
print(f"{player["name"]}进了{player["goals"]}个球")
player["club"]="chelsea"
player["goals"]=20
print(player.keys())

players=[
    {"name":"qi","goals":6,"assists":2},
    {"name":"pf","goals":2,"assists":3},
    {"name":"niu","goals":3,"assists":1}
    ]
print(players[2].values())