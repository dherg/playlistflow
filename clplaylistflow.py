#!/usr/bin/env python3

import requests
import json
import random
import string
import time
import urllib.parse as urlparse
from playlist import Playlist
from track import Track



def authenticateuser():
    """ 
        Send authorization request, get authorization code in uri, use
        code from uri to request access and refresh tokens.
        
        Returns a code or None if some error prevented authentication.
    """
    # read application keys from text file
    with open("keys.txt", "r") as f:
        appid, appsecret, redirecturi = f.read().splitlines()

    # generate random state string for request (for security)
    state = ''.join(random.choice(string.ascii_lowercase
                    + string.digits) for i in range(10))

    # need access to public and private playlists
    scope = ("playlist-read-private playlist-read-collaborative" 
            + " playlist-modify-public playlist-modify-private")

    # load request parameters
    payload = {}
    payload["client_id"] = appid
    payload["response_type"] = "code"
    payload["redirect_uri"] = redirecturi
    payload["state"] = state
    payload["scope"] = scope


    # generate authorization request
    r = requests.get("https://accounts.spotify.com/authorize/",
                    params=payload)
    print('url = \n\n {} \n\n'.format(r.url))

    # parse uri response
    uri = input("callback uri? ")
    parseduri = urlparse.parse_qs(urlparse.urlparse(uri).query)

    # check that state returned is state sent for this request
    if state != parseduri['state'][0]:
        print("error: sent state doesn't match uri returned state!")
        # TODO: serve up some error page

    # get authorization code (or error code) from uri
    if 'code' in parseduri:
        code = parseduri['code'][0]
        return(code)
    else:
        error = parseduri['error'][0]
        return(None)

def getauthenticationurl():
    """ 
        For use as imported function. Generate and return a properly formatted
        authentication URL. 

        Returns the randomly generated state string and an authentication URL
        string, or None, None if a problem is encountered.
    """

    # read application keys from text file
    with open("keys.txt", "r") as f:
        appid, appsecret, redirecturi = f.read().splitlines()

    # generate random state string for request (for security)
    state = ''.join(random.choice(string.ascii_lowercase
                    + string.digits) for i in range(10))

    # need access to public and private playlists
    scope = ("playlist-read-private playlist-read-collaborative" 
            + " playlist-modify-public playlist-modify-private")

    # load request parameters
    payload = {}
    payload["client_id"] = appid
    payload["response_type"] = "code"
    payload["redirect_uri"] = redirecturi
    payload["state"] = state
    payload["scope"] = scope

    # create URL
    r = requests.Request("GET",
                "https://accounts.spotify.com/authorize/",
                params=payload)
    prepped = r.prepare()

    # return state and url
    if state and prepped.url:
        # print("prepped.url: {}".format(prepped.url))
        return(state, prepped.url)
    else:
        return(None, None)

def requesttokens(code):
    """ 
        Exchange authorization code for access and refresh tokens with a POST
        request to /api/token endpoint.

        Returns access token and refresh token, or None,None if unable to 
        obtain tokens.
    """

    print("code = {}".format(code))
    
    with open("keys.txt", "r") as f:
        appid, appsecret, redirecturi = f.read().splitlines()

    payload = {}
    payload["grant_type"] = "authorization_code"
    payload["code"] = code
    payload["redirect_uri"] = redirecturi
    payload["client_id"] = appid
    payload["client_secret"] = appsecret

    r = requests.post("https://accounts.spotify.com/api/token", data=payload)

    response = r.json()

    if "refresh_token" not in response:
        if response["error"]:
            print(response["error"])
            if response["error"]["status"]:
                if response["error"]["status"] == 429:
                    # wait for the amount of time specified in response header
                    time.sleep(int(r.headers["Retry-After"]) + 1)
                    # try again
                    return(requesttokens(code))
                else:
                    print('error: token request failed')
                    print(response["error"])
                    return(None)
            else:
                print('error: token request failed')
                print(response["error"])
                return(None)
        else:
            print(response["error"])
            return(None, None)

    refreshtoken = response["refresh_token"]
    accesstoken = response["access_token"]
    expiration = response["expires_in"]
    # print('\ntokens:\n\n{}'.format(r.json()))

    return(accesstoken, refreshtoken)

def getrequesttokensurl(code):
    """
        Given an authorization code, format and return a POST url to
        /api/token endpoint for access and refresh tokens.

        Returns a URL to request tokens, or None if unsuccessful
    """

    with open("keys.txt", "r") as f:
        appid, appsecret, redirecturi = f.read().splitlines()

    payload = {}
    payload["grant_type"] = "authorization_code"
    payload["code"] = code
    payload["redirect_uri"] = redirecturi
    payload["client_id"] = appid
    payload["client_secret"] = appsecret

    # create URL
    r = requests.Request("POST",
                "https://accounts.spotify.com/api/token",
                data=payload)
    prepped = r.prepare()

    if prepped.url:
        return(prepped.url)
    else:
        return(None)

def getuserid(accesstoken):
    """ 
        Get the current user's id using the /v1/me endpoint.

        Returns user's id as a string, or None if unable to obtain id.
    """

    headers = {}
    headers["Authorization"] = "Bearer {}".format(accesstoken)

    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    # print('response = \n\n {} \n\n'.format(r.text))
    # print('userid:\n\n{}'.format(r.json()))


    response = r.json()
    if "id" not in response:
        if response["error"]:
            if response["error"]["status"] == 429:
                # wait for the amount of time specified in response header
                time.sleep(int(r.headers["Retry-After"]) + 1)
                # try again
                return(getuserid(accesstoken))

            else:
                print(response["error"])
                return(None)
        else:
            print('error: getuserid request failed')
            return(None)

    userid = response["id"]
    # print("userid = {}".format(userid))
    return(userid)

def getplaylists(accesstoken, userid):
    """ 
        Build a dict containing the names, thumbnail URLs, and playlist IDs of
        the current user's playlists using the /v1/me/playlists endpoint.

        API returns a maximum of 50 playlists at a time, so while 50 are
        returned, requests next 50 using the offset API parameter to ensure
        all playlists are found.

        Return a dict with names mapping to playlist objects.
    """
    
    headers = {}
    headers["Authorization"] = "Bearer {}".format(accesstoken)

    limit = 50

    payload = {}
    payload["limit"] = limit
    payload["offset"] = 0

    r = requests.get("https://api.spotify.com/v1/me/playlists",
                        headers=headers, 
                        params=payload)

    # print('url = \n\n {} \n\n'.format(r.url))

    response = r.json()

    # add data to playlist objects
    if "items" not in response:
        if response["error"]:
            if response["error"]["status"] == 429:
                # wait for the amount of time specified in response header
                time.sleep(int(r.headers["Retry-After"]) + 1)
                # try again
                return(getplaylists(accesstoken, userid))

            else:
                print(response["error"])
                return(None)
        else:
            print('error: getplaylists request failed')
            return(None)

    numberreceived = len(response["items"])
    totalavailable = response["total"]

    playlists = {}

    for playlist in response["items"]:
        p = Playlist()
        p.images = playlist["images"]
        p.name = playlist["name"]
        p.playlistid = playlist["id"]
        playlists[p.name] = p

    # if number received less than total available, request more
    while numberreceived < totalavailable:
        # print("received={} available={}".format(numberreceived, totalavailable))
        payload["offset"] = payload["offset"] + limit
        r = requests.get("https://api.spotify.com/v1/me/playlists",
                        headers=headers, 
                        params=payload)
        response = r.json()

        if "items" not in response:
            if response["error"]:
                if response["error"]["status"] == 429:
                    # wait for the amount of time specified in response header
                    time.sleep(int(r.headers["Retry-After"]) + 1)
                    # try again
                    continue
                else:
                    print('error: getplaylists request failed')
                    print(response["error"])
                    return(None)
            else:
                return(None)

        for playlist in response["items"]:
            p = Playlist()
            p.images = playlist["images"]
            p.name = playlist["name"]
            p.playlistid = playlist["id"]
            playlists[p.name] = p

        numberreceived = numberreceived + len(response["items"])

    return(playlists)

def getplaylistchoice(playlists):
    """
        Present user with list of their playlists, and get their choice for
        which playlist they want to be "flowed"

        Returns a single Playlist object representing the chosen playlist, or
        None if there is an error.
    """

    # for testing
    return(playlists["xmu"])

    for i, name in enumerate(playlists):
        print("[{}] {}".format(i, name))

    # assuming input is a playlist, TODO will be a multiple choice
    # checkboxes?
    chosenplaylistname = input("Type the name of the playlist you want to be flowed: ")

    return(playlists[chosenplaylistname])

def getplaylisttracks(accesstoken, chosenplaylist, userid):
    """
        Take a playlist object and fill out its 'tracks' attribute with a list
        of track objects

        Returns a Playlist object with the tracks attribute complete, or None
        if there is an error.
    """

    headers = {}
    headers["Authorization"] = "Bearer {}".format(accesstoken)

    limit = 100

    payload = {}
    payload["limit"] = limit
    payload["offset"] = 0

    playlistid = chosenplaylist.playlistid    

    r = requests.get(
        "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(userid, playlistid),
        headers=headers,
        params=payload)

    response = r.json()

    if "items" not in response:
        if response["error"]:
            if response["error"]["status"] == 429:
                # wait for the amount of time specified in response header
                time.sleep(int(r.headers["Retry-After"]) + 1)
                # try again
                return(getplaylisttracks(accesstoken, chosenplaylist, userid))
            else:
                print(response["error"])
                return(None)
        else:
            print('error: getplaylisttracks request failed')
            return(None)

    numberreceived = len(response["items"])
    totalavailable = response["total"]

    for track in response["items"]:
        t = Track()
        t.trackid = track["track"]["id"]
        t.albumname = track["track"]["album"]["name"]
        t.trackname = track["track"]["name"]
        t.artistname = track["track"]["artists"][0]["name"]
        t.popularity = track["track"]["popularity"]
        # print(t.trackid, t.trackname, t.artistname, t.albumname)
        chosenplaylist.tracks[t.trackid] = t

    # if we haven't gotten all of the tracks in the playlist, request the next
    # batch

    while numberreceived < totalavailable:

        payload["offset"] = payload["offset"] + limit
        r = requests.get(
        "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(userid, playlistid),
        headers=headers,
        params=payload)
        response = r.json()

        if "items" not in response:
            if response["error"]:
                if response["error"]["status"] == 429:
                    # wait for the amount of time specified in response header
                    time.sleep(int(r.headers["Retry-After"]) + 1)
                    # try again
                    continue
                else:
                    print('error: getplaylisttracks request failed')
                    print(response["error"])
                    return(None)
            else:
                print('error: unknown error')
                return(None)

        for track in response["items"]:
            t = Track()
            t.trackid = track["track"]["id"]
            t.albumname = track["track"]["album"]["name"]
            t.trackname = track["track"]["name"]
            t.artistname = track["track"]["artists"][0]["name"]
            # print(t.trackid, t.trackname, t.artistname, t.albumname)
            chosenplaylist.tracks[t.trackid] = t
               
        numberreceived = numberreceived + len(response["items"])

    # print(chosenplaylist.tracks)
    return(chosenplaylist)

def gettrackinfo(accesstoken, playlist):
    """
        Given a playlist object, fills the audio features for each track
        object in the given playlist's list of tracks.

        No return value.
    """

    headers = {}
    headers["Authorization"] = "Bearer {}".format(accesstoken)

    for track in playlist.tracks:

        r = requests.get("https://api.spotify.com/v1/audio-features/{}".format(track),
            headers=headers)

        response = r.json()

        if "danceability" not in response:
            if response["error"]:
                if response["error"]["status"] == 429:
                    # wait correct amount
                    time.sleep(int(r.headers["Retry-After"]) + 1)
                    needinfo = True
                    while needinfo:
                        r = requests.get("https://api.spotify.com/v1/audio-features/{}"
                                        .format(track),
                                        headers=headers)
                        response = r.json()
                        if "danceability" in response:
                            break
                        elif response["error"]:
                            if response["error"]["status"] == 429:
                                # wait
                                time.sleep(int(r.headers["Retry-After"]) + 1)
                                continue
                            else:
                                print('error: gettrackinfo failed')
                                print(response["error"])
                                return(None)
                else:
                    print('error: gettrackinfo failed')
                    print(response["error"])
                    return(None)
            else:
                print('error: gettrackinfo failed')
                print('no error response')
                return(None)

        t = playlist.tracks[track]
        t.danceability = response["danceability"]
        t.energy = response["energy"]
        t.key = response["key"]
        t.loudness = response["loudness"]
        t.mode = response["mode"]
        t.speechiness = response["speechiness"]
        t.acousticness = response["acousticness"]
        t.instrumentalness = response["instrumentalness"]
        t.liveness = response["liveness"]
        t.valence = response["valence"]
        t.tempo = response["tempo"]
        t.duration_ms = response["duration_ms"]
        t.time_signature = response["time_signature"]

        # t.printattributes()

def sortbyflow(playlist):
    """
        Takes in a Playlist object with Tracks filled with attributes, applies
        flow algorithm to group songs (For now just sorts by the valence
        attribute, TODO: something more sophisticated.)

        Returns a list of track URIs in the newly sorted order, or None if
        there is an error.
    """
    try:
        unsortedlist = [playlist.tracks[x] for x in playlist.tracks]

        sortedlist = sorted(unsortedlist, key = lambda x: x.valence)
        sorteduris = ["spotify:track:{}".format(track.trackid) for track in sortedlist]
    except:
        print("error: sorting in sortbyflow failed")
        return(None)

    return(sorteduris)

def createspotifyplaylist(accesstoken, name, playlists, tracklist, userid):
    """
        Use the given tracklist to create a new playlist on spotify with the 
        name "{name} - flowed", or "{name} - flowed (1)" if "{name} - flowed" 
        already exists, or "{name} - flowed ({n})" if "{name} - flowed ({n-1})"
        exists. Takes in playlists (dict of user's playlists) to check whether
        names are taken.

        Returns True if successful, False if unsuccessful.
    """

    # find a unique name for the playlist
    playlistname = "{} - flowed".format(name)
    if playlistname in playlists:
        num = 1
        playlistname = "{} - flowed ({})".format(name, num)
        while playlistname in playlists:
            num = num + 1
            playlistname = "{} - flowed ({})".format(name, num)

    # create playlist
    headers = {}
    headers["Authorization"] = "Bearer {}".format(accesstoken)
    headers["Content-Type"] = "application/json"

    payload = {}
    payload["name"] = playlistname

    url = "https://api.spotify.com/v1/users/{}/playlists".format(userid)

    r = requests.post(url, headers=headers, json=payload)

    response = r.json()


    if "collaborative" not in response:
        if response["error"]:
            if response["error"]["status"] == 429:
                retry = True
                while retry:
                    time.sleep(int(r.headers["Retry-After"]) + 1)
                    r = requests.post(url, headers=headers, json=payload)
                    response = r.json()
                    if response["error"]:
                        if response["error"]["status"] == 429:
                            continue
                        else:
                            print("error: problem creating spotify playlist")
                            print(response["error"])
                            return(False)
                    elif "collaborative" in response:
                        break
                    else:
                        print("error: problem creating spotify playlist")
                        print('no error response')
                        return(False)
            else: 
                print("error: problem creating spotify playlist")
                print(response["error"])
                return(False)
        else:
            print("error: problem creating spotify playlist")
            print('no error response')
            return(False)

    playlistid = response["id"]

    # add tracks to playlist
    while len(tracklist) > 100:
        # print("len(tracklist) = {}".format(len(tracklist)))

        # add first 100
        headers = {}
        headers["Authorization"] = "Bearer {}".format(accesstoken)
        headers["Content-Type"] = "application/json"

        payload = {}
        payload["uris"] = tracklist[:100]

        r = requests.post("https://api.spotify.com/v1/users/{}/playlists/{}/tracks"
                        .format(userid, playlistid),
                        headers=headers,
                        json=payload)

        response = r.json()
        if "snapshot_id" not in response:
            if response["error"]:
                if response["error"]["status"] == 429:
                    time.sleep(int(r.headers["Retry-After"]) + 1)
                    continue
                else:
                    print("error: problem adding songs to playlist")
                    print(response["error"])
                    return(False)
            else:
                print("error: problem adding songs to playlist")
                print("no error response")
                return(False)

        tracklist = tracklist[100:]

    if tracklist:
        print("len(tracklist) = {}".format(len(tracklist)))

        # add the remainder of the tracks
        headers = {}
        headers["Authorization"] = "Bearer {}".format(accesstoken)
        headers["Content-Type"] = "application/json"

        payload = {}
        payload["uris"] = tracklist

        r = requests.post("https://api.spotify.com/v1/users/{}/playlists/{}/tracks"
                        .format(userid, playlistid),
                        headers=headers,
                        json=payload)

        response = r.json()
        if "snapshot_id" not in response:
            if response["error"]:
                if response["error"]["status"] == 429:
                    retry = True
                    while retry:
                        time.sleep(int(r.headers["Retry-After"]) + 1)
                        r = requests.post("https://api.spotify.com/v1/users/{}/playlists/{}/tracks"
                        .format(userid, playlistid),
                        headers=headers,
                        json=payload)
                        response = r.json()
                        if "snapshot_id" in response:
                            break
                        elif response["error"]:
                            if response["error"]["status"] == 429:
                                continue
                            else:
                                print("error: createspotifyplaylist request failed")
                                print(response["error"])
                                return(False)
                        else:
                            print("error: createspotifyplaylist request failed")
                            print("no error response")
                            return(False)
                else:
                    print("error: createspotifyplaylist request failed")
                    print(response["error"])
                    return(False)
            else:
                print("error: createspotifyplaylist request failed")
                print("no error response")
                return(False)

    return(True)
    

def main():

    # get code
    code = authenticateuser()

    # use code to request access and refresh tokens
    accesstoken, refreshtoken = requesttokens(code)

    # get current user id
    userid = getuserid(accesstoken)

    # build dict of playlist objects for user's playlists
    playlists = getplaylists(accesstoken, userid)

    # find out which playlist user wants flowed
    chosenplaylist = getplaylistchoice(playlists)

    # get list of that playlist's tracks
    playlist = getplaylisttracks(accesstoken, chosenplaylist, userid)

    # get info for each of that playlist's tracks
    gettrackinfo(accesstoken, playlist)

    # run flow algorithm to determine correct order
    newtracklist = sortbyflow(playlist)

    # create new playlist with that track order
    createspotifyplaylist(accesstoken, playlist.name, playlists,
                         newtracklist, userid)


if __name__ == "__main__":
    main()