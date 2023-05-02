from flask_spotify_auth import getAuth, refreshAuth, getToken, REFRESH_TOKEN
from flask import session
import requests
import logging
import time
from dotenv import load_dotenv
load_dotenv()
import json
import os
import random as rand
import string as string

# #Add your client ID
# CLIENT_ID = "9f67073037194d00b364265c592004f4"
CLIENT_ID = os.getenv("CLIENT_ID")

# #ADD YOUR CLIENT SECRET FROM SPOTIFY
# CLIENT_SECRET = "386a2545f3434b278fb8e2b708fcf3d6"
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

#Port and callback url can be changed or ledt to localhost:5000

PORT = "5000"
CALLBACK_URL = "http://localhost"

#Add needed scope from spotify user
SCOPE = "streaming user-read-email user-read-private user-top-read playlist-modify-private playlist-modify-public"
#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown 
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, "{}:{}/callback".format(CALLBACK_URL, PORT))
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA[0]

def getRefreshToken():
    return TOKEN_DATA[4]

#-------------------SPOTIFY API CALLS-------------------#
def createStateKey(size):
    return ''.join(rand.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))


def get_request(url, params={}):
    """
    Get a request from the Spotify API.

    Args:
        url (str): The URL to make the request to.
        params (dict): Any parameters to include in the request.
        payload (dict): Any payload to include in the request.

    Returns:
        dict: The JSON response from the request.
    """
    # retrieve access token 
    # with open('token.txt', 'r') as f:
    #     data = f.read()
    #     global TOKEN
    #     TOKEN = json.loads(data)['access_token']
        

    headers = { 'Authorization': 'Bearer {}'.format(TOKEN_DATA[0])}
    request = requests.get(url, headers=headers, params=params)

    if request.status_code == 200:
        return request.json()
    
    # if get error 401 try to refresh token and get new access token
    elif request.status_code == 401:
        refreshToken(5)
        return get_request(url, params)
    
    elif request.status_code == 429:
        print ('get_request:' + str(request.status_code))
        time.sleep(5)
        return None
    
    elif request.status_code == 403:
        print ('get_request:' + str(request.status_code))
        time.sleep(5)
        return None
    
def makePostRequest(url, data):
    """
    Make a POST request to the Spotify API.

    Args:
        url (str): The URL to make the request to.
        data (dict): The data to include in the request.

    Returns:
        dict: The JSON response from the request.
    
    """
    headers= {"Authorization": "Bearer {}".format(TOKEN_DATA[0]), 'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=data)


    if response.status_code == 201:
        return response.json()
    if response.status_code == 204:
        return response

    elif response.status_code == 401:
        refreshToken(5)
        return makePostRequest(url, data)
    elif response.status_code == 403 or response.status_code == 404:
        return response.status_code
    else:
        logging.error('post_request: ' + str(response.status_code))
        return None
        
    
def get_user_profile():
    """
    Get detailed profile information about the current user (including the current users username).

    Returns:  dict:   A dictionary of user information.
    """
    return get_request('https://api.spotify.com/v1/me')


def get_user_top_tracks(limit = 20):
    """
    Get the current user's top tracks.

    Args:
        limit (int): The number of tracks to return. Defaults to 10. Max 50.
        
    Returns: 
        list:   A list of track IDs.
    """
    url = 'https://api.spotify.com/v1/me/top/tracks'
    track_ids = []
    time_range = ['short_term', 'medium_term', 'long_term']

    for time in time_range:
        track_range_ids = []
        params = {'limit': limit, 'time_range': time}
        response = get_request(url, params)
        for item in response['items']:
            track_range_ids.append(item['id'])
        track_ids.append(track_range_ids)
            
    return track_ids
    
def createPlaylist(playlist_name, userid):
    """
    Creates a playlist for the user with the given name.

    Args:
        playlist_name (str): The name of the playlist to create.
        userid (str): The user ID of the user to create the playlist for.

    Returns:
        str: The ID of the created playlist.
        str: The URI of the created playlist.
    
    """
    url = 'https://api.spotify.com/v1/users/' + userid + '/playlists'
    data = "{\"name\":\"" + playlist_name + "\",\"description\":\"Created by KabinAnalyzes\"}"
    response = makePostRequest(url, data)

    if response == None:
        return None
    
    return response['id'], response['uri']

def addTracksPlaylist(playlist_id, uri_list):
    """
    Adds tracks to the given playlist

    Args:
        playlist_id (str): The ID of the playlist to add tracks to.
        uri_list (list): A list of track URIs to add to the playlist.

    Returns:    
        None
    
    """
    url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'
    uri_str = ""
	
    for uri in uri_list:
        uri_str += "\"" + uri + "\","

    data = "{\"uris\": [" + uri_str[0:-1] + "]}"

    makePostRequest(url, data)

    return

def getTopTracksURI(time, limit=25):
    """
    Retrives current user's top tracks URI

    Args:
        time (str): The time range of the top tracks. Can be short_term, medium_term, or long_term.
        limit (int): The number of tracks to return. Defaults to 10. Max 50.

    Returns:
        list: A list of track URIs.
    
    """
    url = 'https://api.spotify.com/v1/me/top/tracks'
    params = {'limit': limit, 'time_range': time}
    response = get_request(url, params)

    if response == None:
        return None
    
    track_uri = []

    for track in response['items']:
        track_uri.append(track['uri'])

    return track_uri
