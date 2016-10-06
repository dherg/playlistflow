# Playlist Flow

[Try it out!](http://playlistflow.herokuapp.com)

For people with eclectic Spotify playlists, Playlist Flow helps  easily reorder songs so that they sound better together.

### The Flow Algorithm

1. Playlist Flow gets [song attributes](https://developer.spotify.com/web-api/get-audio-features/) for each song in a playlist.
2. The attributes are treated as coordinates, and the difference between songs is calcuated as the Euclidean distance between coordinates.
3. With these distances, we can find a path through the songs that keeps the difference between each song small using the [nearest neighbor algorithm](https://en.wikipedia.org/wiki/Nearest_neighbour_algorithm). (Finding _the_ shortest path would be a [harder problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem).)

### Details 

Playlist Flow is a Flask app hosted on Heroku and makes use of the awesome Spotify API. For bugs or suggestions, feel free to open an issue or submit a pull request.
