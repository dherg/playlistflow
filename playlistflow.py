from flask import Flask, render_template, redirect, request
import urllib.parse as urlparse
import clplaylistflow as pf

app = Flask(__name__)

state = None # associate this state with some user, in dict?

@app.route('/')
def index():
    return(render_template('test.html'))

@app.route('/<string:s>')
def string(s):
    return(s)

@app.route('/spotifylogin')
def authenticate():
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
    accesstoken, refreshtoken = pf.requesttokens(code)

    # have tokens, get userid
    userid = pf.getuserid(accesstoken)

    return("userid: {}".format(userid))

def dosomethingelse():
    print('do something else')

if __name__ == "__main__":
    app.debug = True
    # dosomethingelse()
    app.run()
    