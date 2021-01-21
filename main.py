#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import re
import json
import os

url = input("Enter instagram post url: ")

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'
}

try:
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
        exit(0)
except Exception as e:
    print(str(e))
    print("Enter a valid url")
    exit(0)
soup = BeautifulSoup(r.text, 'lxml')
soup.prettify

# To check if the account is private
isPrivate = re.search('"is_private":(\w*)', str(soup)).group(1)
if isPrivate == "true":
    print("Account is private cannot download the data")
    exit(0)

# For number of slides (multi-posts)
pattern = re.compile('"is_video":(\w*)')
videos = list(pattern.finditer(str(soup)))

# To Find the video url
pattern = re.compile('"video_url":"([^"]*)')
videoUrls = list(pattern.finditer(str(soup)))

# To find the image url
pattern = re.compile('"display_url":"([^"]*)')
imageUrls = list(pattern.finditer(str(soup)))


# Final urls list storing in the form of nested list eg. [['img',url],['video','url]]
urls = []

# Finding the title and saving only first five letters
# Using json to display emojis
title = re.search('"caption":"([^"]*)', str(soup))
if title:
    title = title.group(1)
    title = (json.loads('"' + title + '"')).split()[:5]
    title = " ".join(title)

# For strange reasons instagram adds additonal image url of first post in a multi post
# If the list is greater than 1 discard the first one
if len(videos) > 1:
    videos = videos[1:]
    imageUrls = imageUrls[1:]

# Extracting the url and storing in the urls list
# Using json to convert \u0026 to &
print()
for isVideo in videos:
    if isVideo:
        isVideo = isVideo.group(1)
    if isVideo == "true":
        url = videoUrls[0].group(1)
        url = json.loads('"' + url + '"')
        urls.append(['video', url])
        videoUrls.pop(0)
    else:
        url = imageUrls[0].group(1)
        url = json.loads('"' + url + '"')
        urls.append(['img', url])
        imageUrls.pop(0)

# Getting the content and saving it on the local machine
for i, url in enumerate(urls):
    r = requests.get(url[1])
    name = ""
    if url[0] == 'img':
        name = f'{title} ({i}).jpg'
        with open(name, 'wb') as f:
            f.write(r.content)
    else:
        name = f'{title} ({i}).mp4'
        with open(name, 'wb') as f:
            f.write(r.content)
    print("Your file saved at " + os.path.join(os.getcwd(), name))
if not urls:
    print("Enter a valid instagram post link")
