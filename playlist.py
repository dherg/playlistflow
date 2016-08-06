# Playlist class to represent a spotify playlist
# Contains information about the playlist, including playlist id, list of
# tracks, URL to playlist thumbnail, the length of the playlist, and the name
# of the playlist

class Playlist():

	def __init__(self):

		self.tracks = [] # list of trackid's or track objects?
		self.imageurl = None
		self.length = None
		self.name = None
		self.playlistid = None 


