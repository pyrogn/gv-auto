from bs4 import BeautifulSoup

with open("pages/superhero_basic.html") as f:
    page = f.read()

soup = BeautifulSoup(page, features="html.parser")
# print(soup)

print([i.text for i in soup.find_all(class_="d_msg")])
news = soup.find("div", id="news")
print(news.find("h2", class_=["block_title"]).text)
