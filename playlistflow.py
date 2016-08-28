from flask import Flask, render_template, redirect, request, session
from urlparse import urlparse, parse_qs
import os
import clplaylistflow as pf
from user import User

app = Flask(__name__)

# need dict mapping user (by cookie) to data (playlists, track info)
# state = None # associate this state with some user, in dict?
# playlists = None # also in dict
# accesstoken = None
# refreshtoken = None
# userid = None

# session: has cookie for state. e.g. session["state"] = <state>
# global users dict (later redis db): key is <state>, value is user object

users = {}


@app.route('/')
def index():
    return(render_template('index.html'))

@app.route('/spotifylogin')
def authenticate():
    user = User()
    user.state, url = pf.getauthenticationurl()

    # add this user to sessions
    session["state"] = user.state

    # add this user to dict
    users[user.state] = user

    print('sent state {}'.format(user.state))

    return(redirect(url))

@app.route('/callback')
def callback():
    url = request.url
    parseduri = parse_qs(urlparse(url).query)

    # check cookie
    if "state" in session:
        state = session["state"]
        if state != parseduri['state'][0]:
            return('error: sent state ({}) not equal to return state ({})'.format(state, parseduri['state'][0]))
        #print('\n\n{} in session\n\n'.format(parseduri['state'][0]))
    else:
        print('\n\n{} NOT in session\n\n'.format(parseduri['state'][0]))
        # TODO: server error page/ redirect to index

    # get user object from users dict
    if state not in users:
        print('user with state={} not found in user dict. redirecting to index'.format(state))
        return("error: are cookies enabled? if not, try enabling them.")
    user = users[state]

    # get authorization code (or error code) from uri
    if 'code' in parseduri:
        code = parseduri['code'][0]
    else:
        error = parseduri['error'][0]
        return(None)

    user.accesstoken, user.refreshtoken = pf.requesttokens(code)

    # have tokens, get userid
    user.userid = pf.getuserid(user.accesstoken)

    # build dict of user's playlists
    user.playlists = pf.getplaylists(user.accesstoken, user.userid)

    playlistnames = [x for x in user.playlists]


    # find out which playlist is wanted
    return(render_template('playlists.html', playlistnames=playlistnames))

@app.route('/selection')
def selection():

    # check cookie for state
    if "state" in session:
        state = session["state"]
    else:
        print('\n\n{} NOT in session\n\n'.format(parseduri['state'][0]))
        # TODO: server error page/ redirect to index

    # get user object from users dict
    if state not in users:
        print('user with state={} not found in user dict. redirecting to index'.format(state))
        return("error: are cookies enabled? if not, try enabling them.")
    user = users[state]

    if request.args.get('choice'):
        chosenplaylist = user.playlists[request.args.get('choice')]
    else:
        return('error')

    # get list of the playlist's tracks
    playlist = pf.getplaylisttracks(user.accesstoken, chosenplaylist)

    # double check to make sure playlist isn't empty
    if not playlist.tracks:
        return("Looks like the playlist you chose doesn't have any songs in it. Try a different one!")

    # get info for each of that playlist's tracks
    pf.gettrackinfo(user.accesstoken, playlist)

    # run flow algorithm to determine correct order
    newtracklist = pf.sortbyflow(playlist)
    if not newtracklist:
        return('error; newtracklist is None')

    # create new playlist with that track order
    playlistname, url = pf.createspotifyplaylist(user.accesstoken, playlist.name, user.playlists,
                         newtracklist, user.userid)

    return(render_template("result.html", name=playlistname, url=url))
    # return('playlist {} complete - enjoy!'.format(playlist.name))

@app.route('/about')
def about():
    return(render_template("about.html"))

def setappkey():
    app.secret_key = os.environ.get('FLASKSECRET')

# set the app key
setappkey()

if __name__ == "__main__":
    app.debug = True
    app.run(threaded=True, host="0.0.0.0", port=5000)

    