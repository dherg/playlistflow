# User class to keep each user's data (list of playlists, etc.) separate.
# Users identified by randomly generated state

class User():

    def __init__(self, authorizationcode=None, state=None, playlists=None, 
                 accesstoken=None, refreshtoken=None, userid=None):

        self.state = state
        self.playlists = playlists
        self.accesstoken = accesstoken
        self.refreshtoken = refreshtoken
        self.userid = userid


