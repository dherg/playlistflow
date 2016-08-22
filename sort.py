# "Flow" algorithms: simple sort based on an attribute, nearest neighbor

def simpleflow(playlist, attribute="valence"):
    """
        The fastest and most simple flow sort - sort songs based on one of the
        song attributes, from lowest to highest value. Accepts a playlist object
        containing tracks and "attribute" parameter to sort by, which is
        one of the attributes defined in Track object.

        Returns a list of Tracks in sorted order, or None if there is an error
    """
    try:
        unsortedlist = [playlist.tracks[x] for x in playlist.tracks]
        sortedlist = sorted(unsortedlist, key = lambda x: getattr(x, attribute))
    except Exception as e:
        print(e)
        return(None)
    return(sortedlist)
    

def nnflow(playlist):
    """
        Flow using nearest neighbor algorithm. Idea is that differences in
        attribute values between songs are used to compute a 'distance' between
        each song. Creating a playlist with that minimizes the maximum distance
        between any two songs is equivalent to the bottlenect traveling salesman
        problem. One computationally feasible heuristic for this problem is the
        nearest neighbor algorithm: arbitrarily choose a starting node, compute
        the distance from it to all unvisited nodes, then move the closest node
        and continue.

        Accepts a playlist object containing all of the tracks.

        Returns a list of Tracks in sorted order, or None if there is an error
        during the sorting.
    """
    pass

