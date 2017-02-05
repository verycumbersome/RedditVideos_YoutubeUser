import re
import urllib2
try:
    import praw
except:
    lib = "PRAW"
    print "ImportError: %s is not found on your system" % (lib)
    print "You must install %s to operate this program" % (lib)
    sys.exit()

r = praw.Reddit(user_agent="JustDudeStuff_V1",client_secret="AzvrzjEk6y6HL9MaEpKDpNHtbTo",client_id="8FzeKTyVy50rhQ")

def GetTopSubmissions(subreddit, l):
    SubredditInstance = r.subreddit(subreddit)
    TopOfSub = SubredditInstance.top(limit = l)

    UrlList = []
    KarmaList = []
    counter = 0

    for item in TopOfSub:
        match = re.search(r"youtube\.com/.*v=([^&]*)", item.url)

        print item.ups

        if match:
            result = match.group(1)
            UrlList.append(result)
            KarmaList.append(item.ups)
            counter+=1
        else:
            result = ""
    return UrlList, KarmaList
