# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 20:14:10 2018

@author: Aldo Novendi
"""

import requests
from urllib.parse import urlparse, parse_qs
import re, os
import math
import random
from random import randint
import sys
import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = 'AIzaSyD3p0CeMi4xXpoJtY_XetmITZj7J0Ni-3g'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

#input youtube URL
#url = input("Insert Youtube URL: ")
module_dir = os.path.dirname(__file__)
POLARITY_DATA_DIR = os.path.join(module_dir, 'corpus')
SENSING_WORD_FILE = os.path.join(POLARITY_DATA_DIR, 'sensingWordList.txt')

commentCount = 0
sampleSize = 0
commentSample = []
videoID = ''
videoTitle = ''

def getSensingWords():
    sensingWords = []
    
    fp = open(SENSING_WORD_FILE, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        sensingWords.append(word)
        line = fp.readline()
    fp.close()
    
    return sensingWords

def process_comment(comment):
    comment = comment.lower()
    comment = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','', comment)
    comment = re.sub('[!@#$\.,()-_:"]+', ' ', comment)
    comment = re.sub('\s+',' ', comment)
    comment = re.sub('(?:^| )\w(?:$| )',' ', comment)
    comment = comment.strip()
    
    sensingWords = getSensingWords()
    
    try:
        commentWords = comment.split()
    except:
        print('comment is None')
        return
        
    senseAvl = 0
    
    for w in commentWords:
        w = re.sub(r'([a-z])\1+', r'\1', w)
        w = w.strip('\'"?,\.')
        matches = [sw for sw in sensingWords if sw == w]
        if len(matches) > 0:
            senseAvl = 1
            break
    
    if senseAvl == 1:
        return comment
    else:
        return None

#validate youtube URL is in correct format
def launch_youtube(url):
    global commentCount
    global sampleSize
    global commentSample
    global videoID
    global videoTitle
    commentSample = []
    regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
    match = regex.match(url)

    #get video_id
    try:
        videoID = match.group('id')
    except:
        print('It is not a Youtube URL')
        sys.exit(1)

    apiUrl = "https://www.googleapis.com/youtube/v3/commentThreads?key=" + API_KEY + "&textFormat=plainText&order=relevance&part=snippet&videoId=" + videoID + "&maxResults=100"
    try:
        commentThreads = requests.get(apiUrl).json() 
        comments = commentThreads["items"]
    except:
        print("Video doesn't exist")
#        sys.exit(1)
        return

    urlComment = "https://www.googleapis.com/youtube/v3/videos?key=" + API_KEY + "&part=statistics,snippet&id=" + videoID
    commentCount = int(int(requests.get(urlComment).json()["items"][0]["statistics"]["commentCount"])*0.7)
    videoTitle = requests.get(urlComment).json()["items"][0]["snippet"]["title"]
    #print(commentCount)
    
    confLvl = 0.95
    marginError = 0.05
    
    noTop = confLvl*confLvl
    noBot = marginError*marginError
    no = noTop/noBot
    sampleSize = math.ceil(no/(1+no/commentCount));
    #print(sampleSize)
    
    sampleSizePerToken = 25
    if commentCount <= 2000:
        sampleSizePerToken = math.ceil(sampleSize/(math.ceil(commentCount/100)))
        
    sampleIndex = random.sample(range(0,100), sampleSizePerToken)
    #print(sampleIndex);
    #print(sampleSizePerToken)
    #print(comments[0])
    
    commentSample = []
    countPage = 0
    while sampleSize>0 and countPage < 10:
        countPage += 1
        if(sampleSize < sampleSizePerToken):
            sampleSizePerToken = sampleSize
        if sampleSize < 100:
            sampleIndex = random.sample(range(0,sampleSize), sampleSizePerToken)
#        print(countPage, sampleIndex)
  
        for i in range(0, sampleSizePerToken):
            try:
                commentSample.append(comments[sampleIndex[i]]["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
            except:
                print('index out of range')
                continue
            
        try:
            nextPageToken = commentThreads["nextPageToken"]
            apiUrl = "https://www.googleapis.com/youtube/v3/commentThreads?key=" + API_KEY + "&textFormat=plainText&order=relevance&part=snippet&videoId=" + videoID + "&maxResults=100&pageToken=" + nextPageToken
            commentThreads = requests.get(apiUrl).json() 
            comments = commentThreads["items"]
        except:
            print("Last page")
            break

        sampleSize -= sampleSizePerToken