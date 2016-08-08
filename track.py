# Track class to represent a spotify track
# Contains information about the track, like track id and audio features about
# the track obtained from the /audio-features endpoint

class Track():

    def __init__(self):

        self.trackid = None
        self.trackname = None
        self.artistname = None
        self.albumname = None
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

    def printattributes(self):

        print("trackid: {trackid}\n\t"
            "trackname: {trackname}\n\t" 
            "artistname: {artistname}\n\t"
            "albumname: {albumname}\n\t"
            "danceability: {danceability}\n\t"
            "energy: {energy}\n\t"
            "key: {key}\n\t" 
            "loudness: {loudness}\n\t"
            "mode: {mode}\n\t"
            "speechiness: {speechiness}\n\t"
            "acousticness: {acousticness}\n\t"
            "instrumentalness: {instrumentalness}\n\t"
            "liveness: {liveness}\n\t"
            "valence: {valence}\n\t"
            "tempo: {tempo}\n\t"
            "duration_ms: {duration_ms}\n\t"
            "time_signature: {time_signature}"
            .format(trackid=self.trackid,
                trackname=self.trackname,
                artistname=self.artistname,
                albumname=self.albumname,
                danceability=self.danceability,
                energy=self.energy,
                key=self.key,
                loudness=self.loudness,
                mode=self.mode,
                speechiness=self.speechiness,
                acousticness=self.acousticness,
                instrumentalness=self.instrumentalness,
                liveness=self.liveness,
                valence=self.valence,
                tempo=self.tempo,
                duration_ms=self.duration_ms,
                time_signature=self.time_signature
            )
        )
