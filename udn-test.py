from urllib.request import urlopen
from bs4 import BeautifulSoup
page = 0
while True:
    url = "https://udn.com/news/get_breaks_article/"+str(2+page)+"/1/99?_="+str(1547385778403+page)
    print("處理第", page + 2, "頁")
    response = urlopen(url)
    html = BeautifulSoup(response)
    if len(html) == 0:
        print("應該爬完了")
        break
    page = page + 1
    for a in html.find_all("dt",class_="lazyload"):
        category = a.find("a",class_="cate")
        title = a.find("h2")
        times = a.find("div",class_="dt")
        view = a.find("div",class_="view")
        newsurl = a.find("a")
        Nresponse = urlopen("https://udn.com"+newsurl["href"])
        Nhtml = BeautifulSoup(Nresponse)
        print(category.text, times.text, title.text, view.text, "https://udn.com" + newsurl["href"])
        for content in Nhtml.find("div", id="story_body_content").find_all("p"):
            print(content.text)

