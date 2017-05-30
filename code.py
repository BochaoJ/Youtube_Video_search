import urllib
import urllib2
from bs4 import BeautifulSoup
import requests
import re
import pandas
from lxml import etree
from decimal import Decimal

## search key words
textToSearch = 'Funny Vines'
query = urllib.quote(textToSearch)
url = "https://www.youtube.com/results?search_query=" + query
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html)
count=0
filesInChannel = []
for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    web = 'https://www.youtube.com' + vid['href']
    if "watch" in web:
      filesInChannel.append(web)
      count=count+1


## retrive number of like, dislike, views and title for each video.
def getStats(link):
    page = requests.get(link)
    views = int(filter(str.isdigit, re.search("(\d*.\d*.\d*) views", page.text).group(1).encode("utf-8")))
    likes = int(filter(str.isdigit, re.search("like this video along with (\d*.\d*.\d*)", page.text).group(1).encode("utf-8")))
    dislikes = int(filter(str.isdigit, re.search("dislike this video along with (\d*.\d*.\d*)", page.text).group(1).encode("utf-8")))
    youtube = etree.HTML(urllib.urlopen(link).read())
    title = ''.join(youtube.xpath("//span[@id='eow-title']/@title"))
    return (likes, dislikes, views, round(Decimal(likes)/dislikes,5), round(Decimal(likes)/views,5), round(Decimal(likes+dislikes)/views,5), title,link)

stats = []
for link in filesInChannel:
    stats.append(getStats(link))

## summarize the information and sort it by the ratio of #likes/#dislikes.

df = pandas.DataFrame(stats)
my_columns = ["likes", "dislikes", "views","ratio likes/dislikes", "ratio likes/views", "comments ratio", "title", "url link"]
df.columns = my_columns


table = df.sort_values(by=['ratio likes/dislikes','ratio likes/views','views','comments ratio'], ascending=False)
table.to_csv("video.csv")

