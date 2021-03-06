import YoutubeChannelFinder
import TopReddit
import argparse
import threading
import json
import datetime
import threading

from itertools import chain
from datetime import datetime
from collections import Counter, OrderedDict
from deepdiff import DeepDiff

parser = argparse.ArgumentParser(description='argparser for Python code')
parser.add_argument('-l', '--limit', help='sets subreddit top get limit', type=int, default=1000)
parser.add_argument('-s', '--subreddit', help='sets subreddit from which to get top youtube users', default="videos")
parser.add_argument('-p', '--postnumber', help='sets the number of videos to post to subreddit', type=int, default=8)
parser.add_argument('-y', '--karmalimit', help='sets the minimum subscriber value for Youtube in order for it to be posted to subreddit', type=int)
args = parser.parse_args()

currentdate=datetime.today()
timedifference=currentdate.replace(year=currentdate.year, month=currentdate.month, day=currentdate.day, hour=currentdate.hour, minute=currentdate.minute, second=0, microsecond=0)
currentdate, timedifference
delta_t=currentdate-timedifference

secs=delta_t.seconds

def getTopYoutuberList(postJSON):

    UrlLists, Klist, PostUrl = TopReddit.GetTopSubmissions(args.subreddit, args.limit)
    counter = 1
    usercounter = 0
    additionalRequests = 0

    userList = []
    OrderedDictionary = {}
    MostRecentYoutubePost = []
    MostRecentYoutubeName = []
    YoutubeUsername = []


    for items in UrlLists:
        if counter<len(UrlLists):
            try:
                YoutubeUser = {YoutubeChannelFinder.GetUserNameFromId(UrlLists[counter]):Klist[counter]}

                userList.append(YoutubeUser)

            except IndexError:
                YoutubeUser = 'null'
            print counter, "/", len(UrlLists), YoutubeUser
            counter +=1
        else:
            None

    #Appends all karma scores in dictionary to one key per user
    for dictionary in userList:
        for key, value in dictionary.items():
            if OrderedDictionary.has_key(key):
                OrderedDictionary[key] = value + OrderedDictionary[key]

            else:
                OrderedDictionary[key] = value

    postFreq = Counter(OrderedDictionary.items())

    #Sorts the dictionary of all Youtube channel IDs by the associated karma value
    x = Counter(OrderedDictionary)
    y = OrderedDict(x.most_common())

    while (usercounter <= (args.postnumber + additionalRequests)):
        try:
            #Finds the uploads playlist for the userList
            YoutubeChannel = YoutubeChannelFinder.GetMostRecentVideo(y.keys()[usercounter])

            #Finds the most recent video from the uploads playlist
            recentId = YoutubeChannelFinder.GetMostRecentPlaylistVideo(YoutubeChannel)

            #Finds the subscriber count on Youtube of the channel
            subCount = int(YoutubeChannelFinder.GetSubCountFromId(y.keys()[usercounter]))

            #VideoId for recent posts from playlist 'uploads'
            MostRecentYoutubePost.append(recentId[0])

            #Video names for recent posts in playlist 'uploads'
            MostRecentYoutubeName.append(recentId[1])

            category = YoutubeChannelFinder.GetCategoryId(MostRecentYoutubePost[usercounter])

            print usercounter, recentId[1], y.values()[usercounter], YoutubeChannelFinder.GetUserFromId(MostRecentYoutubePost[usercounter]), subCount, YoutubeChannelFinder.GetCategoryId(MostRecentYoutubePost[usercounter])

            #filter for channel making it to approved submitters
            if subCount>30000 and category not in ["Entertainment", "Howto & Style", "News & Politics", "Sports"] and y.values()[usercounter]>10000:
                YoutubeUsername.append({YoutubeChannelFinder.GetUserFromId(MostRecentYoutubePost[usercounter]): MostRecentYoutubePost[usercounter]})

                if postJSON:
                    with open('data/youtubers.json', 'w') as outfile:
                        json.dump(YoutubeUsername, outfile, sort_keys = True, indent = 4)

                print "valid", usercounter
            else:
                additionalRequests+=1
                print "invalid"

            usercounter += 1

        except IndexError:
            break

    return YoutubeUsername

def postList():
    with open("data/youtubers.json") as yList:
        youtuberList = json.load(yList)

    for items in youtuberList:
        TopReddit.PostTopSubmissions(items.keys()[0], YoutubeChannelFinder.GetVidNameFromId(items.values()[0]), items.values()[0])
        print YoutubeChannelFinder.GetVidNameFromId(items.values()[0])

def getDiff():
    youtubers1 = getTopYoutuberList(False)
    with open("data/youtubers.json") as yList:
        youtubers = json.load(yList)

    if bool(DeepDiff(youtubers, youtubers1)):
        for items in DeepDiff(youtubers, youtubers1, ignore_order=True)['iterable_item_added'].values():
            print items.values()[0]
            TopReddit.PostTopSubmissions(items.keys()[0], YoutubeChannelFinder.GetVidNameFromId(items.values()[0]), items.values()[0])
        getTopYoutuberList(True)

        print "The Dict is different"

    else:
        print "The Dict is not different"

    try:
        t = threading.Timer(10, getDiff)
        t.start()
    except KeyboardInterrupt:
        t.cancel()

getTopYoutuberList(True)
postList()
getDiff()
