# -*- coding: UTF-8 -*-
#^ keep that as the first line of the file.
#mxb130530&smd170030
import urllib
import json
import zen
import sys
sys.path.append('../zend3js/')
import d3js
import colorsys
import unicodedata
#http://json.parser.online.fr/
import time

import pycurl
from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#DATA STRUCTURE KEY:
#artist_ids_CUML = list of all album id's added to the graph. useful for indexing and comparing their arrays.

#FUNCTION DEFINITIONS_________________________________________________
#gets the spotify web api html info at that URL
def get_URL(URL):
	f=urllib.urlopen(URL)
	string = f.read()
	f.close
	return string


def play_artist(artistid):
	prefix='https://play.spotify.com/artist/'
	suffix = '?play=true'
	musicURL=prefix+artistid+suffix
	driver.get(musicURL)
	if (artistid =='3TVXtAsR1Inumwj472S9r4'):
		driver.find_element_by_xpath('//*[@id="fb-signup-btn"]').click()
	return





#get artist albums: need artist id
def get_albums(artist_id, limit):
	prefix= 'https://api.spotify.com/v1/artists/'
	suffix='/albums?album_type=album&market=US&limit='
	URL=prefix+artist_id+suffix+limit
	album_string=get_URL(URL)
	json_albums=json.loads(album_string)
	if (json_albums['total']>int(limit)):
		num_albums=int(limit)
	else:
		num_albums=json_albums['total']
	album_ids = list()
	album_names=list()
	substring1='(Deluxe)'
	substring2 = '(Deluxe Edition)'

	for i in range (0,num_albums):
		indicator1=1
		indicator2=1
		#make sure you don't load the copy cat albums:
		curr_album_name=json_albums['items'][i]['name']
		
		curr_album_id=json_albums['items'][i]['id']
		if (i==0): #no need to check
			album_ids.append(json_albums['items'][i]['id'])	#a list to store all album id's
			album_names.append(json_albums['items'][i]['name'])#a list to store all album nam
		elif (curr_album_name.endswith(substring1)): #replace smaller/older album with deluxe version
			curr_album_name_trunc=curr_album_name[:-9]
		elif (curr_album_name.endswith(substring2)):
			curr_album_name_trunc=curr_album_name[:-17]
			for j in range(0,len(album_names)):
				if (album_names[j]==curr_album_name_trunc or album_names[j]==curr_album_name):
					album_names[j]=curr_album_name
					album_ids[j]=album_ids[j]
					indicator1=0
			if (indicator1==1and album_names[j]):
				album_ids.append(curr_album_id)
				album_names.append(curr_album_name)

		else: #make sure we only get one album of each name.
			for k in range (0, len(album_names)):
				if (curr_album_name == album_names[k]):
					indicator2=0
				if (indicator2==1):
					album_ids.append(curr_album_id)	#a list to load all album id's
					album_names.append(curr_album_name)
		if (len(album_ids)>20):
			for r in range(20, len(album_ids)):
				album_ids.pop(20)
	return (album_ids)

def get_tracks(main_artist, main_artist_id, album_ids,G,artist_ids_CUML):
	main_artist =unicodedata.normalize('NFKD',main_artist.strip().decode('utf-8')).encode('ascii','ignore')
	album_ids_str=','.join(album_ids)
	prefix='https://api.spotify.com/v1/albums?ids='
	suffix='&market=US'
	URL=prefix+album_ids_str+suffix
	tracks_string=get_URL(URL)
	json_track=json.loads(tracks_string)
	m=0 #album counter
	if (json_track.get('albums')): #only if the artist has albums
		for m in range (0,len(json_track['albums'])): #loop through all of artist's albums
			for n in range (0, len (json_track['albums'][m]['tracks']['items'])):#loop through all songs on album
				curr_track_name=json_track['albums'][m]['tracks']['items'][n]['name']
				for p in range(0,len(json_track['albums'][m]['tracks']['items'][n]['artists'])):#loop all artist in each song
					indicator3=1
					curr_track_artist=json_track['albums'][m]['tracks']['items'][n]['artists'][p]['name']
					curr_track_artist=curr_track_artist.encode('utf-8') #because we may add this to graph.
					curr_track_artist=unicodedata.normalize('NFKD',curr_track_artist.strip().decode('utf-8')).encode('ascii','ignore')
					curr_track_artist_id=json_track['albums'][m]['tracks']['items'][n]['artists'][p]['id']
					curr_track_artist_id=unicodedata.normalize('NFKD',curr_track_artist_id.strip().decode('utf-8')).encode('ascii','ignore')
					if (curr_track_artist_id!=main_artist_id):
						for q in range (0, G.num_nodes):
							if (artist_ids_CUML[q]==curr_track_artist_id):#make sure id is not in graph
								indicator3=0
						for t in range(0, (G.num_nodes)):
							if (G.nodes()[t]==curr_track_artist and artist_ids_CUML[t]!=curr_track_artist_id): #give newer one a numerical id at end of name.
								curr_track_artist =curr_track_artist+curr_track_artist_id
						if (indicator3==1):
							G.add_node(curr_track_artist)
							artist_ids_CUML.append(curr_track_artist_id)
							d3.update()
						if (G.has_edge(main_artist, curr_track_artist)):
							if (G.weight(main_artist, curr_track_artist)==0):#because of edge directionality
								G.add_edge(main_artist, curr_track_artist)
							else:
								w=G.weight(main_artist, curr_track_artist)
								G.set_weight(main_artist, curr_track_artist, w+1)
						else:
							G.add_edge(main_artist, curr_track_artist)
	d3.update()
	return (artist_ids_CUML, G)

def read_file(fname): #open file with names of artists from billboard list: http://www.billboard.com/charts/year-end/2016/hot-r-and-and-b-hip-hop-songs
	artist = 'empty'#initialize as string
	file=open(fname, 'r')
	prefix ='https://api.spotify.com/v1/search?q='
	suffix='&type=artist'
	with open(fname) as f:
		for i, l in enumerate(f):
			artist= file.readline()
			artist =unicodedata.normalize('NFKD',artist.strip().decode('utf-8')).encode('ascii','ignore')
			G.add_node(artist)#add the node, the node didnt exist yet.
			d3.update()
			URL=prefix+str(artist)+suffix
			artist_string=get_URL(URL)
			json_artist=json.loads(artist_string)
			#can pick the first one[0] since in snowballing out, we are wanting the most popular drake or 'X'
			curr_artist_id=json_artist['artists']['items'][0]['id']
			curr_artist_id=curr_artist_id.encode('utf-8')
			artist_ids_CUML.append(curr_artist_id)
	return (G.num_nodes)

#____________________________________________MAIN FILE_____________________________________________

#graph basics
G=zen.DiGraph()
d3 = d3js.D3jsRenderer(G, event_delay=0.1, interactive=False, autolaunch=True)

#read file
fname='start_art.txt' #will be more dynamic when we build the file
limit = '50'#size limiting number of albums we return; spotify API maximum
maxart = 2000 #max number artists
artist_ids_CUML = list()
num_orig_nodes= read_file(fname)
layer_size=G.num_nodes #for starters
h=0
layer_count=1

#login to fb so that we can auto log into spotify.
driver = webdriver.Chrome('/Users/mallorybing/Downloads/chromedriver')
username='bingdelpak@gmail.com'
password='pythonbot'
spotify_login_enabler ='https://www.facebook.com/'
driver.get(spotify_login_enabler);
search_box = driver.find_element_by_xpath('//*[@id="email"]')
search_box.send_keys(username)
search_box.send_keys(Keys.TAB)
search_box = driver.find_element_by_xpath('//*[@id="pass"]')
search_box.send_keys(password)
search_box.submit()#done with fb


while (h<10):#max number artists to ADD
	print G.nodes()[h]
	play_artist(artist_ids_CUML[h])
	album_ids=get_albums(artist_ids_CUML[h],limit) #get the artist's albums
	artist_ids_CUML,G=get_tracks(G.nodes()[h],artist_ids_CUML[h], album_ids,G,artist_ids_CUML) #get the artist's tracks
	time.sleep(10)
	if (h==layer_size):
		layer_count=layer_count+1
		layer_size=G.num_nodes #size of network to search to search 2nd degree artist's neighbors
		print 'Starting new layer: ', layer_count, '.'
		print 'Checking the previous layer added ', G.num_nodes-1, 'nodes.'
	

	driver.get('https://play.spotify.com/')
	h=h+1

driver.quit()

print 'num nodes' ,G.num_nodes, 'DONE'
print 'len art CUML', len(artist_ids_CUML)



zen.io.gml.write(G,'my.gml')

