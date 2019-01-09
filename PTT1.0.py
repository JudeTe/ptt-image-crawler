from bs4 import BeautifulSoup
import requests
import random
from urllib.request import urlopen , urlretrieve
import os
Pages = random.randint(1500,2600)
Jude = int(input("請輸入想要的頁數："))
Route = input("請輸入想放的路徑，如按Enter則預設為C槽")
Name = input("這邊可以指定您想要放入的資料夾名稱，如按Enter則預設為'Dbeauty'，如已有同名稱之資料夾，圖片會被覆蓋喔！")
Types = input("請輸入想抓的看板：")
if Name == "" :
    Name = "Dbeauty"
for op in range(Pages,Pages+Jude):
    response = requests.get("https://www.ptt.cc/bbs/"+Types+"/index"+str(op)+".html")
    html = BeautifulSoup(response.text)        #以上三行為抓取文章的網址
    b = []
    B2 = []
    # with open("Beauty.txt","w",encoding="utf-8") as file:
    page = 0
    # while page < 1:

    for x in html.find_all("div",class_="title") :
        print(x)
        print("====="*10000)
        try:
            title = x.find("a")["href"]
            print(title)
            print("=====" * 10000)
        except:
            continue
        b.append(title)
        # page += 1
    print("-----")
    print(b)
    c = []
    page2 = 0

    while page2 < 1:
        src = "https://www.ptt.cc"+str(b[page2])
        page2+=1
        response = requests.get(src)
        html = BeautifulSoup(response.text)
        # print(html)
        for d in html.find_all("div",class_="richcontent"):
            try:
                img = d.find("a",)["href"]
                # print(img)
                if Route == "" :
                    dir = "C:/"+Name+"/"
                else :
                    dir = str(Route)+"/"+Name+"/"

                if not os.path.exists(dir):
                    os.mkdir(dir)
                # else :
                #     dir2 = dir+"1/"
                #     os.mkdir(dir2)
                a = dir+"/"+img.split("/")[-1]+".jpg"
                c = img.split("/")[-2]+"/"+img.split("/")[-1]
                c2 = "https://"+c+".jpg"
                print(c2)
                # urlretrieve(c2,a) 是否只能放文字檔？
                with open(a, "wb") as files:
                    files.write(requests.get(c2).content)
            except:
                continue
print(Pages)
