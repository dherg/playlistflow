# Playlist class to represent a spotify playlist
# Contains information about the playlist, including playlist id, list of
# tracks, URLs to playlist thumbnails, the length of the playlist, and the name
# of the playlist

class Playlist():

    def __init__(self):

        self.tracks = [] # list of track objects for tracks in playlist
        self.images = None
        self.length = None
        self.name = None
        self.playlistid = None 
        self.ownerid = None

    def __str__(self):

        return("playlistid:{}".format(self.playlistid))

