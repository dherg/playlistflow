from flask import Flask, render_template, redirect, request, session
from urlparse import urlparse, parse_qs
import os
import redis
import pickle
import logging
import clplaylistflow as pf
from user import User

app = Flask(__name__)
r = redis.from_url(os.environ.get("REDIS_URL"))

logging.basicConfig(filename="app.log", level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    logger.debug('route: /')
    return(render_template('index.html'))

@app.route('/spotifylogin')
def authenticate():
    logger.debug('route: /spotifylogin')
    user = User()
    user.state, url = pf.getauthenticationurl()

    # clear old session
    session.clear()

    # add this user to sessions
    session["state"] = user.state

    # pickle and add to redis
    userpickle = pickle.dumps(user)
    r.setex(user.state, userpickle, 3600) # expire in an hour

    logger.debug('sent state {}'.format(user.state))

    return(redirect(url))

@app.route('/callback')
def callback():
    logger.debug('route: /callback')
    url = request.url
    parseduri = parse_qs(urlparse(url).query)

    # check cookie
    if "state" in session:
        state = session["state"]
        if state != parseduri['state'][0]:
            return('error: sent state ({}) not equal to return state ({})'.format(state, parseduri['state'][0]))
    else:
        logger.debug('\n\n{} NOT in session\n\n'.format(parseduri['state'][0]))
        return("error: are cookies enabled? if not, try enabling them.")
        # TODO: server error page/ redirect to index

    # get user object from redis
    userpickle = r.get(state)
    if not userpickle:
        return('no user with state {} in DB'.format(state))
    else:
        user = pickle.loads(userpickle)
        r.expire(state, 3600) # extend life of user in redis

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

    # write updated user object back to redis
    userpickle = pickle.dumps(user)
    r.setex(user.state, userpickle, 3600)

    playlistnames = [x for x in user.playlists]


    # find out which playlist is wanted
    return(render_template('playlists.html', playlistnames=playlistnames))

@app.route('/selection')
def selection():
    logger.debug('route: /selection')

    # check cookie for state
    if "state" in session:
        state = session["state"]
    else:
        logger.debug('\n\n{} NOT in session\n\n'.format(parseduri['state'][0]))
        return("error: are cookies enabled? if not, try enabling them.")
        # TODO: server error page/ redirect to index

    # get user object from redis
    userpickle = r.get(state)
    if not userpickle:
        return('no user with state {} in DB'.format(state))
    else:
        user = pickle.loads(userpickle)
        r.expire(state, 3600) # extend life of user in redis

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
    logger.debug('route: /about')
    return(render_template("about.html"))

def setappkey():
    app.secret_key = os.environ.get('FLASKSECRET')

# set the app key
setappkey()

if __name__ == "__main__":
    app.debug = True
    app.run(threaded=True, host="0.0.0.0", port=5000)

    