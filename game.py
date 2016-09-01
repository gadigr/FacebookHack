import facebook
import urllib
import urlparse
import subprocess
import warnings
import dateutil.parser

# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Parameters of your app and the id of the profile you want to mess with.
FACEBOOK_APP_ID     = '300827270282284'
FACEBOOK_APP_SECRET = '08dff50d3f19c3f1a7a5862a2c4ff2b1'
FACEBOOK_PROFILE_ID = '10154758587264341'
# HackTest app user id = 1283318901687249
# hacktest app_id = 300827270282284
# hacktest secret = 08dff50d3f19c3f1a7a5862a2c4ff2b1
# Anderson user ID = 10202249303870575

# Trying to get an access token. Very awkward.
oauth_args = dict(client_id     = FACEBOOK_APP_ID,
                  client_secret = FACEBOOK_APP_SECRET,
                  grant_type    = 'client_credentials')
oauth_curl_cmd = ['curl',
                  'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
oauth_response = subprocess.Popen(oauth_curl_cmd,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE).communicate()[0]

try:
    oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
except KeyError:
    print('Unable to grab an access token!')
    exit()

facebook_graph = facebook.GraphAPI(oauth_access_token)

user_access_token = 'EAAERmc6VfCwBAHsTbaPlYsXfPdkqcqnF0vOFqHRpsOcYylesQN1bpoAeNGdGZC95eSnF94nzhaBZC3P5pIBxhlgRstZCTjxcwEo5ZAOnAfKkZBx2tIcmZBjdB4ehzDbn4rbyp07hcnnzNTlnPNLFwAgVkJprj3syRypC8vu6jxMQZDZD'
# page_access_token = 'EAAERmc6VfCwBAHWOiiaiBisijq4SDQBqwjrF1hI02T2JVKqYi7ZCBjt6H2pOdAUATy6R3gZB9rTsGaiWJMFrMRZBZAPtSAhnirZAAeAE37D75lcQmhyRfZCj8atv7pbhJfZAhu8NdfAOMjjIIbwS9ZCoGvHMMT3G1nXkvAQ4tdfDrwZDZD'
# page_access_token = 'EAAERmc6VfCwBAHyCqtueHB23jZAQQkd7NiffO2YKkT6zUQ4RIu8nMv5d2rLI3ZCDiJaFQydhV0cKAR6ZCLwYMzwcygd811TabTtIhIZAxgbZAZBzZAOfcB2XtYRXmOW9LEfLbwY7iIoZChYJchesr4Bnkmf1MZBpJwAVavGHWMEyaYQZDZD'

#create facebook live video
# print(facebook_graph.get_object("me"))

# print(facebook_graph.request('/me/picture', args={'access_token':user_access_token}))

# get profile pic by id
def getProfilePic( profileId ):
    return facebook_graph.request("/%s/picture?height=120" % (profileId),  args={'access_token':user_access_token})

# get last post
last_post =facebook_graph.request("/1283318901687249/feed", args={'access_token':user_access_token})['data'][0]["id"]

last_comment_time =  dateutil.parser.parse(facebook_graph.request('/%s/comments' % (last_post), args={'access_token':user_access_token})["data"][3]["created_time"])

def getCommentsAfter(post, lastCommentTime):
    comments = facebook_graph.request('/%s/comments' % (post), args={'access_token':user_access_token})["data"]
    comments = filter(lambda c: dateutil.parser.parse(c["created_time"]) > lastCommentTime, comments)
    return(comments)

getCommentsAfter(last_post, last_comment_time)
# get last comments for post
# def getLastComments():





## Post something on wall
# fb_response = facebook_graph.put_wall_post('Hello from Python', profile_id = FACEBOOK_PROFILE_ID)
