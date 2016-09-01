import facebook
import urllib
import urlparse
import subprocess
import warnings

# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
warnings.filterwarnings('ignore', category=DeprecationWarning)


# Parameters of your app and the id of the profile you want to mess with.
FACEBOOK_APP_ID     = '300827270282284'
FACEBOOK_APP_SECRET = '08dff50d3f19c3f1a7a5862a2c4ff2b1'
FACEBOOK_PROFILE_ID = '10202249303870575'


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

#user_access_token = 'EAACN9GbqRgIBAGC0NFxOoe9hh4jZBsLn0RJKAdI30JJIoVTZCBbZBToWZBlmO593GWfUHrZAwIFfkfZBeO4VOhPp5ZArs8jZAnQ7ycequisdNYjFzxi40Wdd98a5ZAUWbUrk5zWn9S6JQAGHmmg7SJOIE43Y0Lrgo2AIZD'
page_access_token = 'EAAERmc6VfCwBAHWOiiaiBisijq4SDQBqwjrF1hI02T2JVKqYi7ZCBjt6H2pOdAUATy6R3gZB9rTsGaiWJMFrMRZBZAPtSAhnirZAAeAE37D75lcQmhyRfZCj8atv7pbhJfZAhu8NdfAOMjjIIbwS9ZCoGvHMMT3G1nXkvAQ4tdfDrwZDZD'

# Anderson user ID = 10202249303870575

#create facebook live video
facebook_graph.request('/10202249303870575/live_videos', post_args={'access_token':user_access_token})

## Post something on wall
# fb_response = facebook_graph.put_wall_post('Hello from Python', profile_id = FACEBOOK_PROFILE_ID)
