#!/usr/bin/env python3

import requests
import json
import random
import string
import urllib.parse as urlparse


def authenticateuser():
	""" send authorization request, get authorization code in uri, use
		code from uri to request access and refresh tokens
		
		returns a code or None if some error prevented autherntication
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

def requesttokens(code):
	""" Exchange authorization code for access and refresh tokens with a POST
		request to /api/token endpoint

		returns access token and refresh token or None,None
	"""

	with open("keys.txt", "r") as f:
		appid, appsecret, redirecturi = f.read().splitlines()

	payload = {}
	payload["grant_type"] = "authorization_code"
	payload["code"] = code
	payload["redirect_uri"] = redirecturi
	payload["client_id"] = appid
	payload["client_secret"] = appsecret

	r = requests.post("https://accounts.spotify.com/api/token", data=payload)

	postresponse = r.json()

	if "refresh_token" not in postresponse:
		print('error: token request failed')
		return(None, None)

	refreshtoken = postresponse["refresh_token"]
	accesstoken = postresponse["access_token"]
	expiration = postresponse["expires_in"]
	print('\ntokens:\n\n{}'.format(r.json()))


	return(accesstoken, refreshtoken)

def main():

	# get code
	code = authenticateuser()

	# use code to request access and refresh tokens
	accesstoken, refreshtoken = requesttokens(code)

	# use these codes to 

if __name__ == "__main__":
	main()