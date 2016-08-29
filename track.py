# Track class to represent a spotify track
# Contains information about the track, like track id and audio features about
# the track obtained from the /audio-features endpoint

class Track():

    def __init__(self):

        self.trackid = None
        self.trackname = None
        self.artistname = None
        self.albumname = None
        self.popularity = None
        self.danceability = None
        self.energy = None
        self.key = None
        self.loudness = None
        self.mode = None
        self.speechiness = None
        self.acousticness = None
        self.instrumentalness = None
        self.liveness = None
        self.loudness = None
        self.valence = None
        self.tempo = None
        self.duration_ms = None
        self.time_signature = None
        self.normalizedlist = None # a list of attribute values, normalized to
                                   # float from[0.0, 1.0] for sensible 
                                   # comparison
        self.normtotal = None

    def createnormalizedlist(self):

        # initialize list
        self.normalizedlist = []

        # list of weights to give each attribute
        weights = [3, # danceability
                   3, # energy
                   1, # mode
                   1, # speechiness
                   2, # acousticness
                   1, # instrumentalness
                   1, # liveness
                   0.1, # loudness
                   3, # valence
                   1, # tempo
                    ]

        # danceability [0,1] ; 1 more danceable
        self.normalizedlist.append(self.danceability * weights[0])

        # energy [0,1] ; 1 more energetic
        self.normalizedlist.append(self.danceability * weights[1])

        # mode 0 or 1. 0 minor 1 major
        self.normalizedlist.append(self.mode * weights[2])

        # speechiness [0,1] 1 more speechy
        self.normalizedlist.append(self.speechiness * weights[3])

        # acousticness [0,1] 1 more acoustic
        self.normalizedlist.append(self.acousticness * weights[4])

        # instrumentalness [0,1] 1 more instrumental
        self.normalizedlist.append(self.instrumentalness * weights[5])

        # liveness [0,1] 1 more likely performed live
        self.normalizedlist.append(self.liveness * weights[6])

        # loudness around [-60, 0], larger numbers louder
        self.normalizedlist.append(((self.loudness + 60) / 60) * weights[7])

        # valence [0,1] 1 sounds more positive
        self.normalizedlist.append(self.valence * weights[8])

        # tempo, most probably in range of 60 - 180 or so
        self.normalizedlist.append(self.tempo / 180 * weights[9])

        # add total sum
        self.normtotal = sum(self.normalizedlist)


    def __str__(self):

        return("trackid:{}".format(self.trackid))

    def printattributes(self):

        print("trackid: {trackid}\n\t"
            "trackname: {trackname}\n\t" 
            "artistname: {artistname}\n\t"
            "albumname: {albumname}\n\t"
            "popularity: {popularity}\n\t"
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
                popularity=self.popularity,
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
