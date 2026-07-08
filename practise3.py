players = [
    {"name": "Messi", "goals": 25},
    {"name": "Mbappe", "goals": 22},
    {"name": "Haaland", "goals": 30}
]
for player in players:
    print(f"球员:{player['name']},进球:{player['goals']}")

maxgoal=0
bestname=""
for player in players:
    if player["goals"]>maxgoal:
        maxgoal=player["goals"]
        bestname=player["name"]
print(f"金靴得主{bestname},进球{maxgoal}个")

for player in players:
    if player["goals"]>20:
        print(f"{player['name']}进球效率高，值得买断")