import facebook
import urllib
import urlparse
import subprocess
import warnings
import dateutil.parser
import io
import datetime

import pygame, math, random, pygame.gfxdraw, imutils, json, itertools, threading, time
from pygame.locals import *
from PIL import Image, ImageOps

load_rlock = threading.RLock()

mask = Image.open('images/mask.png').convert('L')
spaceShip = Image.open('images/missile.png')

# SCREEN
WIDTH = 1280
HEIGHT = 720
FPS = 60

# GENERAL
BACK = (204, 255, 255)
bg = pygame.image.load("back5.png")
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

COLLISION_DIST = 65

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

# user_access_token = 'EAAERmc6VfCwBAHsoshLf9stQl3oNOSVf5ubgsR4O0gvZCxiQSbbS6ZA3LUdQtR493UWeUVTp3zqSrnUZBRdKHnDWA6WMyZCa45yvZA05Y1yOegF57HZBmw9BT16FZBNB1JE5C2ZBUfK05CalOcxTAG4Xk7TMBjvBNRKcHjxLITuYOgZDZD'
user_access_token = 'EAAERmc6VfCwBAPQ3ssd7ILb8YAKKCdSZBRfYGhZCdlLKggoSVLZAFfUltWR5Nv7BNKJcgjSYw4EocnhKxzyoO6GCaWZAuoKPDKdTyqMacUasSxeyfppYvTB1Gp2xY9Ttu4lYWzCGJV4ITs8XH239yZBIV4K1INsS4iyikixNwiwZDZD'


done = False

# get profile pic by id
def getProfilePicAsync( profileId ):
	global profilePicturesDict
	if profileId in profilePicturesDict: return
	def async_action():
		profilePicturesDict[profileId] = 'dummy'
		with load_rlock:
			image_str = facebook_graph.request("/%s/picture?height=120" % (profileId),  args={'access_token':user_access_token})
			image_file = io.BytesIO(image_str["data"])
			#profilePicturesDict[profileId] = pygame.image.load(image_file)
			try:
				profilePicturesDict[profileId] = transform_image(pygame.image.load(image_file))
				print('finished loading ' + profileId)
			except Exception as ex:
				print(ex)
				if profileId in profilePicturesDict:
					del profilePicturesDict[profileId]

	t = threading.Thread(target=async_action)
	t.start()

def transform_image(img):
	pil_string = pygame.image.tostring(img, "RGBA", False)
	pil_img = Image.frombytes("RGBA", tuple(img.get_rect()[2:]), pil_string)
	output = ImageOps.fit(pil_img, mask.size, centering=(0.5, 0.5))
	output.putalpha(mask)
	finalPic = Image.new("RGBA",(500,220))
	finalPic.paste(spaceShip,(0,80))
	finalPic.paste(output.rotate(-45),(200,0),output.rotate(-45))
	finalPic = finalPic.resize((250, 110))
	return pygame.image.fromstring(finalPic.tobytes("raw", 'RGBA'), finalPic.size, 'RGBA')
	#return img


# get last post
last_post =facebook_graph.request("/1283318901687249/feed", args={'access_token':user_access_token})['data'][0]["id"]

try:
	# last_comment_time =  dateutil.parser.parse(facebook_graph.request('/%s/comments' % (last_post), args={'access_token':user_access_token})["data"][0]["created_time"])
	list_comments = facebook_graph.request('/%s/comments' % (last_post), args={'access_token':user_access_token})["data"]
	last_comment_time = dateutil.parser.parse(max(list_comments, key = lambda x: dateutil.parser.parse(x["created_time"]))["created_time"])

except Exception as ex:
	print(ex)
	last_comment_time = dateutil.parser.parse(facebook_graph.request("/1283318901687249/feed", args={'access_token':user_access_token})['data'][0]["created_time"])





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

	# pos = [660, 485]
	pos = [903, 510]
	angle = math.pi

	users = []

	shots = []

	potential_enemies = []

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
		if (check_comments % 5 == 0):
			check_comments = 0
			# check for new comments

			# new_comments = getCommentsAfter(last_post, last_comment_time)
			new_comments = list(comments)
			#comments = []
			while (len(comments) > 0):
				comments.pop()

			for i in new_comments:
				#users.append(i["from"]["id"])
				potential_enemies.append(i["from"]["id"])

			if(len(new_comments) > 0):
				last_comment_time = dateutil.parser.parse(new_comments[0]["created_time"])

		new_potential = []
		for potential in potential_enemies:
			if (potential not in profilePicturesDict):
				getProfilePicAsync(potential)
				new_potential.append(potential)
			elif profilePicturesDict[potential] == 'dummy':
				new_potential.append(potential)
			else:
				x = 0
				y = random.choice(ENTRY_POINTS)
				ang = math.atan2(pos[1] - y, pos[0] - x)
				enemies.append({'ang': ang, 'x': x, 'y': y, 'pic': profilePicturesDict[potential]})

		potential_enemies = new_potential
		#i=0
        #
		#for p in users:
		#	i = i+1
		#	if p not in profilePicturesDict:
		#		getProfilePicAsync(p)

		#i = 0
		#for u in  profilePicturesDict.keys():
		#	if (profilePicturesDict[u] != 'dummy'):
		#		screen.blit(profilePicturesDict[u], (i * 120, 20))
		#	i += 1

		for shot in shots:
			# pygame.draw.circle(screen, SHOT, (map(int, [shot['x'], shot['y']])), 5, 0)
			screen.blit(cannon_ball, (map(int, [shot['x'] - 0.5*cannon_ball.get_rect()[2], shot['y']- 0.5*cannon_ball.get_rect()[3]])))
			shot['x'] += SHOT_SPEED * math.cos(shot['ang'])
			shot['y'] += SHOT_SPEED * math.sin(shot['ang'])

		for enemy in enemies:
			#pygame.draw.circle(screen, ENEMY, map(int, [enemy['x'], enemy['y']]), 15, 0)
			w, h = enemy['pic'].get_rect()[2:]
			screen.blit(enemy['pic'], map(int, [enemy['x'] - w / 2, enemy['y'] - h / 2]))
			enemy['x'] += ENEMY_SPEED * math.cos(enemy['ang'])
			enemy['y'] += ENEMY_SPEED * math.sin(enemy['ang']) + random.random() * 10 - 5
			if (enemy['x'] >= WIDTH):
				life -= 1

		white = (255, 255, 255)
		A = font.render('A', True, white)
		screen.blit(A, (0, ENTRY_POINTS[0]))
		B = font.render('B', True, white)
		screen.blit(B, (0, ENTRY_POINTS[1]))
		C = font.render('C', True, white)
		screen.blit(C, (0, ENTRY_POINTS[2]))
		D = font.render('D', True, white)
		screen.blit(D, (0, ENTRY_POINTS[3]))

		text = font.render(str(life), True, CANNON)
		screen.blit(text, (0, 0))

		#if (random.random() <= 0.1):
		#	x = 0
		#	y = random.choice(ENTRY_POINTS)
		#	ang = math.atan2(pos[1] - y, pos[0] - x)
		#	enemies.append({'ang': ang, 'x': x, 'y': y})

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
