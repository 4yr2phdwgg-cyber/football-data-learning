#message="leo messi"
#print(message.upper())
#print(message.lower())
#print(message.replace("leo","messi"))
#print(message.find("messi"))

#name=input("请输入用户名")
#print(f"欢迎您，{name}")

#name=input("请输入您的姓名：")
#age=input("请输入您的年龄：")
#home=input("请输入您的家乡")
#print("\n---自我介绍---")
#print(f"大家好，我叫{name}")
#(f"我今年{age}岁了")
#print(f"我来自{home}")

from datetime import datetime as date
bron=input("请输入您的出生日期")
bron=int(bron)
today=date.now().strftime("%Y")
today=int(today)
age=today-bron
print(f"您今年{age}岁")

