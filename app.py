from flask import Flask, render_template, request, redirect, url_for, session
import startup
import requests
import json

app = Flask(__name__, template_folder='templates')

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/authenticate')
def index():
    response = startup.getUser()
    return redirect(response)

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/tracks')
def tracks():
    if startup.getAccessToken() == None:
        # refresh token
        startup.refreshToken(5)

    user = startup.get_user_profile()
    userid = user['id']
    track_ids = startup.get_user_top_tracks()

    if track_ids == None:
        return render_template('index.html', error = 'Error getting tracks')

    return render_template('tracks.html', track_ids= track_ids, userid=userid)

@app.route('/callback')
def callback():
    startup.getUserToken(request.args['code'])
    return redirect(url_for('home'))

@app.route("/information")
def information():
    return render_template('information.html')

@app.route('/tracks/topplaylist',  methods=['POST'])
def createTopPlaylist():

    #save id's incase autoupdate is chosen
    playlist_id_short = None    
    playlist_id_medium = None
    playlist_id_long = None
    playlist_uri = ""

    #get user id
    user = startup.get_user_profile()
    userid = user['id']

    if 'short_term' in request.form:
        playlist_id_short, playlist_uri = startup.createPlaylist(request.form['short_term_name'], userid)
        uri_list = startup.getTopTracksURI('short_term', 50)
        startup.addTracksPlaylist(playlist_id_short, uri_list)


    if 'medium_term' in request.form:
        playlist_id_medium, playlist_uri = startup.createPlaylist(request.form['medium_term_name'], userid)
        uri_list = startup.getTopTracksURI('medium_term', 50)
        startup.addTracksPlaylist(playlist_id_medium, uri_list)

    if 'long_term' in request.form:
        playlist_id_long, playlist_uri = startup.createPlaylist(request.form['long_term_name'], userid)
        uri_list = startup.getTopTracksURI('long_term', 50)
        startup.addTracksPlaylist(playlist_id_long, uri_list)

    # temp solution
    if 'auto_update' in request.form:
        with open('user_data.json', 'r+') as f:
            # save userid and playlist id's and refresh token as dict
            dict = {}
            dict['userid'] = userid
            dict['playlist_id_short'] = playlist_id_short
            dict['playlist_id_medium'] = playlist_id_medium
            dict['playlist_id_long'] = playlist_id_long
            dict['refresh_token'] = startup.getRefreshToken()
            f.write(json.dumps(dict))
            f.close()
    return playlist_uri

@app.route('/create')
def create():
    return render_template('create.html')

