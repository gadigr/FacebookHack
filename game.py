import facebook
import urllib
import urlparse
import subprocess
import warnings

import pygame, math, random, pygame.gfxdraw, imutils, json, itertools
from pygame.locals import *

# SCREEN
WIDTH = 1024
HEIGHT = 600
FPS = 60

# GENERAL
BACK = (204, 255, 255)
FORE = (0, 255, 0)

# ENTITIES
CANNON = (200, 50, 50)
SHOT = (50, 200, 50)
ENEMY = (50, 50, 200)

# DEFs
SHOT_SPEED = 4
ENEMY_SPEED = 3
ANG_SPEED = math.pi / 100
RADIUS = 50
COLLISION_DIST = 20

ENTRY_POINTS = [125, 375, 625, 875]

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Tahoma", 40, False, False)


def game_main():
	done = False
	
	pos = [920, 150]
	angle = math.pi
	
	shots = []
	
	enemies = []
	
	active = {}
	
	life = 15
	
	while (not done):
		screen.fill(BACK)
		pygame.draw.circle(screen, CANNON, pos, 8, 0)
		pygame.draw.line(screen, CANNON, pos, [pos[0] + math.cos(angle) * RADIUS, pos[1] + math.sin(angle) * RADIUS])
		
		for shot in shots:
			pygame.draw.circle(screen, SHOT, (map(int, [shot['x'], shot['y']])), 5, 0)
			shot['x'] += SHOT_SPEED * math.cos(shot['ang'])
			shot['y'] += SHOT_SPEED * math.sin(shot['ang'])
		
		for enemy in enemies:
			pygame.draw.circle(screen, ENEMY, map(int, [enemy['x'], enemy['y']]), 15, 0)
			enemy['x'] += ENEMY_SPEED * math.cos(enemy['ang'])
			enemy['y'] += ENEMY_SPEED * math.sin(enemy['ang'])
			if (enemy['x'] >= WIDTH):
				life -= 1
		
		text = font.render(str(life), True, CANNON)
		screen.blit(text, (0, 0))
		
		if (random.random() <= 0.02):
			x = 0
			y = random.random() * HEIGHT
			minang = math.atan2(-y, WIDTH - x)
			maxang = math.atan2(HEIGHT - y, WIDTH - x)
			ang = random.random() * (maxang - minang) + minang
			enemies.append({'ang': ang, 'x': x, 'y': y})
		
		for (shot, enemy) in itertools.product(shots, enemies):
			if (dist(shot, enemy) <= COLLISION_DIST):
				shot['x'] = enemy['x'] = -1		
		
		shots = filter(inbounds, shots)
		enemies = filter(inbounds, enemies)
		
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
				shots.append({'ang': angle, 'x': pos[0] + RADIUS * math.cos(angle), 'y': pos[1] + RADIUS * math.sin(angle)})
				del active[key]
			elif key == pygame.K_DOWN:
				angle -= ANG_SPEED
			elif key == pygame.K_UP:
				angle += ANG_SPEED
		 
		pygame.display.flip()
		clock.tick(FPS)

def outofbounds(loc):
	return loc['x'] < 0 or loc['x'] > WIDTH or loc['y'] < 0 or loc['y'] > HEIGHT
	
def inbounds(loc):
	return not outofbounds(loc)

def dist(o1, o2):
	return math.sqrt(math.pow(o1['x'] - o2['x'], 2) + math.pow(o1['y'] - o2['y'], 2))
	
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
	
	print('https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args))
	
	try:
		oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
	except KeyError:
		print('Unable to grab an access token!')
		exit()
	
	facebook_graph = facebook.GraphAPI(oauth_access_token)
	
	user_access_token = 'EAAERmc6VfCwBAH8Uir1jIwtl5y4EZAadxgEWlXs7frFZAdwubJN4ZAce6SWxM5Ewk2n5GR9UOdj2ZAv1ptUkqrZBdvD0zqJ3IpmVZAavnXDE1VRv5kZCyuR329pMHpUsAe72TCwdZABxoEcNTMhTdCYxFKb2kgDmcIMfQKtNZBTExqAZDZD'
	page_access_token = 'EAAERmc6VfCwBAHWOiiaiBisijq4SDQBqwjrF1hI02T2JVKqYi7ZCBjt6H2pOdAUATy6R3gZB9rTsGaiWJMFrMRZBZAPtSAhnirZAAeAE37D75lcQmhyRfZCj8atv7pbhJfZAhu8NdfAOMjjIIbwS9ZCoGvHMMT3G1nXkvAQ4tdfDrwZDZD'
	
	# Anderson user ID = 10202249303870575
	
	print(facebook_graph.request('/me/picture', {'access_token': user_access_token}))
	
	#create facebook live video
	#facebook_graph.request('/10202249303870575/live_videos', post_args={'access_token':page_access_token})
	print('ook')
	## Post something on wall
	# fb_response = facebook_graph.put_wall_post('Hello from Python', profile_id = FACEBOOK_PROFILE_ID)


#facebook_stuff()	
game_main()
