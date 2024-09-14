from bs4 import BeautifulSoup
import json

with open("interp.html") as fh:
    html = BeautifulSoup(fh.read())

with open("hexagrams.json") as fh:
    hexagrams = json.load(fh)
yijing = {}
k = ""
for i,tag in enumerate(html.tbody.find_all("td")):
    if i % 4 == 0:
        cont = tag.contents[0]
        (idx, rest) = cont.split(" ", 1)
        (hexa, rest) = rest.split(" ", 1)
        (left, right) = rest.split(" ", 1)
        trad = left.replace("(", "")
        pinyin = right.replace(")", "")
        k = int(idx)
        yijing[k] = {"hex": hexa, "trad": trad, "pinyin": pinyin}
        print(idx)
        hexidx = [h for h in hexagrams if hexagrams[h][0] == k][0]
        hexagrams[hexidx][1] = hexa
    elif i % 4 == 1:
        yijing[k]["simp"] = tag.contents[0]
    elif i % 4 == 2:
        yijing[k]["decision"] = ""
        for content in tag.contents:
            if not content:
                continue
            yijing[k]["decision"] += (
                str(content)
                  .replace("<br />", "\n")
                  .replace("<p>", "")
                  .replace("</p>", "")
                  .replace("<br/>", "")
            )
    else:
        yijing[k]["interpretation"] = ""
        for content in tag.contents:
            if not content:
                continue
            yijing[k]["interpretation"] += (
                str(content)
                  .replace("<br />", "\n")
                  .replace("<p>", "")
                  .replace("</p>", "")
                  .replace("<br/>", "")
            )
with open("yijing.json", "w") as fh:
    json.dump(yijing, fh, indent=2)

with open("hexagrams.json", "w") as fh:
    json.dump(hexagrams, fh, indent=2)
