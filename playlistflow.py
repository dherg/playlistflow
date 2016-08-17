from flask import Flask, render_template, redirect, request
import urllib.parse as urlparse
import clplaylistflow as pf

app = Flask(__name__)

# need dict mapping user (by cookie) to data (playlists, track info)
state = None # associate this state with some user, in dict?
playlists = None # also in dict
accesstoken = None
refreshtoken = None
userid = None

@app.route('/')
def index():
    return(render_template('index.html'))

@app.route('/<string:s>')
def string(s):
    return(s)

@app.route('/spotifylogin')
def authenticate():
    global state
    state, url = pf.getauthenticationurl()
    # print(url)
    return(redirect(url))

@app.route('/callback')
def callback():
    url = request.url
    parseduri = urlparse.parse_qs(urlparse.urlparse(url).query)
    # check that state returned is state sent for this request
    if state != parseduri['state'][0]:
        print("error: sent state doesn't match uri returned state!")
        # TODO: serve up some error page

    # get authorization code (or error code) from uri
    if 'code' in parseduri:
        code = parseduri['code'][0]
    else:
        error = parseduri['error'][0]
        return(None)
    global accesstoken
    global refreshtoken
    accesstoken, refreshtoken = pf.requesttokens(code)

    # have tokens, get userid
    global userid
    userid = pf.getuserid(accesstoken)

    # build dict of user's playlists
    global playlists
    playlists = pf.getplaylists(accesstoken, userid)

    playlistnames = [x for x in playlists]

    # find out which playlist is wanted
    return(render_template('playlists.html', playlistnames=playlistnames))

@app.route('/selection')
def selection():
    if request.args.get('choice'):
        chosenplaylist = playlists[request.args.get('choice')]
    else:
        return('error')

    # get list of the playlist's tracks
    playlist = pf.getplaylisttracks(accesstoken, chosenplaylist)

    # get info for each of that playlist's tracks
    pf.gettrackinfo(accesstoken, playlist)

    # run flow algorithm to determine correct order
    newtracklist = pf.sortbyflow(playlist)
    if not newtracklist:
        return('error; newtracklist is None')

    # create new playlist with that track order
    pf.createspotifyplaylist(accesstoken, playlist.name, playlists,
                         newtracklist, userid)

    return('playlist {} complete - enjoy!'.format(playlist.name))

if __name__ == "__main__":
    app.debug = True
    app.run()
    