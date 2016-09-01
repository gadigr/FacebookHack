import facebook
import urllib
import urlparse
import subprocess
import warnings
import dateutil.parser
import io

import pygame, math, random, pygame.gfxdraw, imutils, json, itertools, threading, time
from pygame.locals import *

# SCREEN
WIDTH = 1024
HEIGHT = 768
FPS = 60

# GENERAL
BACK = (204, 255, 255)
bg = pygame.image.load("back3.png")
cannon_ball = pygame.image.load("ball.png")
cannon_pic = pygame.image.load("cannon.png")
FORE = (0, 255, 0)

# ENTITIES
CANNON = (200, 50, 50)
SHOT = (50, 200, 50)
ENEMY = (50, 50, 200)

# DEFs
SHOT_SPEED = 4
ENEMY_SPEED = 3
ANG_SPEED = math.pi / 100

RADIUS = 125

profilePicturesDict = {}

COLLISION_DIST = 25

ENTRY_POINTS = [75, 225, 375, 525]


pygame.init()
pygame.font.init()

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

user_access_token = 'EAAERmc6VfCwBAF7nj1ssQm4M3Qr0YFA4485dR7z9XIaoqkqaOrAbpgBccEe9jh0mJBVP3siDJ89SEQO2fViy3rMofTgvYLwtd1kWFQzbguJ7SAmx7EBt9YgOyt75NwhREzNEIuecVFMZCHZAlstnSuW3Ff30xIZBzio7XhaEQZDZD'
user_access_token = 'EAAERmc6VfCwBAF7nj1ssQm4M3Qr0YFA4485dR7z9XIaoqkqaOrAbpgBccEe9jh0mJBVP3siDJ89SEQO2fViy3rMofTgvYLwtd1kWFQzbguJ7SAmx7EBt9YgOyt75NwhREzNEIuecVFMZCHZAlstnSuW3Ff30xIZBzio7XhaEQZDZD'

done = False

# get profile pic by id
def getProfilePicAsync( profileId ):
	global profilePicturesDict
	if profileId in profilePicturesDict: return
	def async_action():
		profilePicturesDict[profileId] = 'dummy'
		image_str = facebook_graph.request("/%s/picture?height=120" % (profileId),  args={'access_token':user_access_token})
		image_file = io.BytesIO(image_str["data"])
		profilePicturesDict[profileId] = pygame.image.load(image_file)

	t = threading.Thread(target=async_action)
	t.start()

# get last post
last_post =facebook_graph.request("/1283318901687249/feed", args={'access_token':user_access_token})['data'][0]["id"]

last_comment_time =  dateutil.parser.parse(facebook_graph.request('/%s/comments' % (last_post), args={'access_token':user_access_token})["data"][3]["created_time"])

def getCommentsAfter(post, lastCommentTime):
	comments = facebook_graph.request('/%s/comments' % (post), args={'access_token':user_access_token})["data"]
	comments = filter(lambda c: dateutil.parser.parse(c["created_time"]) > lastCommentTime, comments)
	return(comments)

def getUserByComment(comment):
	return comment["from"]["id"]

def start_loading_comments(post, where_to_save_to, last_comment_time):
	global done
	def load(last_comment_time):
		while not done:
			comments = facebook_graph.request('/%s/comments' % (post), args={'access_token':user_access_token})["data"]
			comments = filter(lambda c: dateutil.parser.parse(c["created_time"]) > last_comment_time, comments)
			if(len(comments) > 0):
					last_comment_time = dateutil.parser.parse(comments[0]["created_time"])
			for new_comment in comments:
				where_to_save_to.append(new_comment)
			time.sleep(1)

	t = threading.Thread(target=load, args=(last_comment_time,))
	t.start()

def rot_center(image, angle):
    # """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

# get last comments for post
# def getLastComments():

	## Post something on wall
	# fb_response = facebook_graph.put_wall_post('Hello from Python', profile_id = FACEBOOK_PROFILE_ID)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Tahoma", 40, False, False)

def game_main():
	global last_comment_time
	global profilePicturesDict
	global done
	global cannon_pic

	check_comments = 0

	pos = [660, 485]
	angle = math.pi

	users = []

	shots = []

	enemies = []

	active = {}

	comments = []

	life = 15

	start_loading_comments(last_post, comments, last_comment_time)

	while (not done):
		# screen.fill(BACK)
		screen.blit(bg, (0, 0))
		# pygame.draw.circle(screen, CANNON, pos, 8, 0)
		pygame.draw.line(screen, CANNON, pos, [pos[0] + math.cos(angle) * RADIUS, pos[1] + math.sin(angle) * RADIUS])
		#cannon_pic2 = rot_center(cannon_pic, angle*180/math.pi)
		ang = -angle * 180/math.pi + 180
		#w, h = cannon_pic.get_rect()[2:]
		cannon_pic2 = pygame.transform.rotate(cannon_pic, ang)
		w, h = cannon_pic2.get_rect()[2:]
		#screen.blit(cannon_pic2, pos)
		screen.blit(cannon_pic2, (pos[0] - w / 2, pos[1] - h / 2))
		#screen.blit(cannon_pic2, (pos[0] + w * math.cos(ang) + (h / 2) * math.sin(ang), pos[1] + w * math.sin(ang) + (h/2) * math.cos(ang)))

		# image = getProfilePic(10207479332124589)
		# screen.blit(image, (20,20))

		check_comments = check_comments+1
		if (check_comments % 120 == 0):
			check_comments = 0
			# check for new comments

			#new_comments = getCommentsAfter(last_post, last_comment_time)
			new_comments = list(comments)
			#comments = []
			while (len(comments) > 0):
				comments.pop()

			for i in new_comments:
				users.append(i["from"]["id"])

			if(len(new_comments) > 0):
				last_comment_time = dateutil.parser.parse(new_comments[0]["created_time"])

		i=0

		for p in users:
			i = i+1
			#image = getProfilePic(p)
			#screen.blit(image, (i*120, 20))
			#def show_me(what):
				#screen.blit(what, (i * 20, 20))
			getProfilePicAsync(p)


		#print(profilePicturesDict.keys())
		i = 0
		for u in  profilePicturesDict.keys():
			if (profilePicturesDict[u] != 'dummy'):
				screen.blit(profilePicturesDict[u], (i * 120, 20))
			i += 1

		for shot in shots:
			# pygame.draw.circle(screen, SHOT, (map(int, [shot['x'], shot['y']])), 5, 0)
			screen.blit(cannon_ball, (map(int, [shot['x'] - 0.5*cannon_ball.get_rect()[2], shot['y']- 0.5*cannon_ball.get_rect()[3]])))
			shot['x'] += SHOT_SPEED * math.cos(shot['ang'])
			shot['y'] += SHOT_SPEED * math.sin(shot['ang'])

		for enemy in enemies:
			pygame.draw.circle(screen, ENEMY, map(int, [enemy['x'], enemy['y']]), 15, 0)
			enemy['x'] += ENEMY_SPEED * math.cos(enemy['ang'])
			enemy['y'] += ENEMY_SPEED * math.sin(enemy['ang'])
			if (enemy['x'] >= WIDTH):
				life -= 1

		A = font.render('A', True, (0, 0, 0))
		screen.blit(A, (0, ENTRY_POINTS[0]))
		B = font.render('B', True, (0, 0, 0))
		screen.blit(B, (0, ENTRY_POINTS[1]))
		C = font.render('C', True, (0, 0, 0))
		screen.blit(C, (0, ENTRY_POINTS[2]))
		D = font.render('D', True, (0, 0, 0))
		screen.blit(D, (0, ENTRY_POINTS[3]))

		text = font.render(str(life), True, CANNON)
		screen.blit(text, (0, 0))

		if (random.random() <= 0.1):
			x = 0
			y = random.choice(ENTRY_POINTS)
			ang = math.atan2(pos[1] - y, pos[0] - x)
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

game_main()
#facebook_stuff()
