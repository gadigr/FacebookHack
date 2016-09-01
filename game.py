import facebook
import urllib
import urlparse
import subprocess
import warnings

import pygame, math, random, pygame.gfxdraw, imutils, json
from pygame.locals import *

WIDTH = 1024
HEIGHT = 600
BACK = (204, 255, 255)
FORE = (0, 255, 0)

FPS = 60

CANNON = (200, 50, 50)
SHOT = (50, 200, 50)

SHOT_SPEED = 2

ANG_SPEED = math.pi / 100
RADIUS = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()
pygame.font.init()


def game_main():
	done = False
	
	pos = [920, 150]
	angle = math.pi
	
	shots = [] # {ang: ??, x: ??, y: ??}
	
	active = {}
	while (not done):
		screen.fill(BACK)
		pygame.draw.circle(screen, CANNON, pos, 8, 0)
		pygame.draw.line(screen, CANNON, pos, [pos[0] + math.cos(angle) * RADIUS, pos[1] + math.sin(angle) * RADIUS])
		
		for shot in shots:
			pygame.draw.circle(screen, SHOT, (map(int, [shot['x'], shot['y']])), 5, 0)
			shot['x'] += SHOT_SPEED * math.cos(shot['ang'])
			shot['y'] += SHOT_SPEED * math.sin(shot['ang'])
		
		#pos[0] += 1
		#pos[1] += 1
		
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				active[event.key] = True
			elif event.type == pygame.KEYUP and event.key in active:
				del active[event.key]
			elif event.type == pygame.QUIT:
				done = True
				
		for key in active.keys():
			if key == pygame.K_ESCAPE:
				done = True
			elif key == pygame.K_SPACE:
				shots.append({'ang': angle, 'x': pos[0], 'y': pos[1]})
				del active[event.key]
			elif key == pygame.K_DOWN:
				angle -= ANG_SPEED
			elif key == pygame.K_UP:
				angle += ANG_SPEED
		 
		pygame.display.flip()
		clock.tick(FPS)

game_main()
		
def facebook_stuff():
	# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
	warnings.filterwarnings('ignore', category=DeprecationWarning)
	
	
	# Parameters of your app and the id of the profile you want to mess with.
	FACEBOOK_APP_ID	 = '300827270282284'
	FACEBOOK_APP_SECRET = '08dff50d3f19c3f1a7a5862a2c4ff2b1'
	FACEBOOK_PROFILE_ID = '10202249303870575'
	
	
	# Trying to get an access token. Very awkward.
	oauth_args = dict(client_id	 = FACEBOOK_APP_ID,
					client_secret = FACEBOOK_APP_SECRET,
					grant_type	= 'client_credentials')
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
