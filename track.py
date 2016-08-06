# Track class to represent a spotify track
# Contains information about the track, like track id and audio features about
# the track obtained from the /audio-features endpoint

class Track():

    def __init__(self):

        self.trackid = None
        self.danceability = None
        self.energy = None
        self.key = None
        self.loudness = None
        self.mode = None
        self.speechiness = None
        self.acousticness = None
        self.instrumentalness = None
        self.liveness = None
        self.valence = None
        self.tempo = None
        self.duration_ms = None
        self.time_signature = None

    def __str__(self):

        return("trackid:{}".format(self.trackid))
