# "Flow" algorithms: simple sort based on an attribute, nearest neighbor
import sys
import math

def simpleflow(playlist, attribute="valence"):
    """
        The fastest and most simple flow sort - sort songs based on one of the
        song attributes, from lowest to highest value. Accepts a playlist object
        containing tracks and "attribute" parameter to sort by, which is
        one of the attributes defined in Track object. O(n log n)

        Returns a list of Tracks in sorted order, or None if there is an error
    """
    try:
        unsortedlist = playlist.tracks
        sortedlist = sorted(unsortedlist, key = lambda x: getattr(x, attribute))
    except Exception as e:
        print(e)
        return(None)
    return(sortedlist)

def fastnnflow(playlist, size=50, attribute="valence"):
    """
        The normal nnflow nearest neighbor sort can take a long time. This sort
        tries to speed it up a bit by first sorting tracks roughly based on some
        attribute (e.g. valence), then breaking the list of songs up into
        segments of "size" length, doing a nearest neighbor sort within those 
        segments, and concatenating the results. Accepts a playlist object, a
        segment size, and an attribute by which to do initial rough sort.

        Returns a list of Tracks in sorted order, or None if there is an error.
    """

def nnflow(playlist):
    """
        Flow using nearest neighbor algorithm. Idea is that differences in
        attribute values between songs are used to compute a 'distance' between
        each song. Creating a playlist with that minimizes the maximum distance
        between any two songs is equivalent to the bottlenect traveling salesman
        problem (without returning to the original song). One computationally 
        feasible heuristic for this problem is the nearest neighbor algorithm: 
        arbitrarily choose a starting node, compute the distance from it to all 
        unvisited nodes, then move the closest node and continue. O(n^2)

        Accepts a playlist object containing all of the tracks.

        Returns a list of Tracks in sorted order, or None if there is an error
        during the sorting.
    """
    unsortedlist = playlist.tracks
    sortedlist = []

    # normalize and get total values for each track. keep track of lowest total
    # so as to start playlist with that track (hopefully will avoid large jump
    # in middle of playlist that way.. if start at random track in middle,
    # likely to move to outside ranges, then end up jumping back to middle
    # tracks)
    minimumval = float('inf')
    minimumindex = None
    for i, track in enumerate(unsortedlist):
        track.createnormalizedlist()
        if track.normtotal < minimumval:
            minimumval = track.normtotal
            minimumindex = i

    # remove that track and use it as current to start
    currenttrack = unsortedlist.pop(minimumindex)
    sortedlist.append(currenttrack)

    while len(unsortedlist) > 1:
        # find closest to currenttrack by iterating through
        closesttrackindex = None
        closesttrackdistance = float('inf')
        for i, track in enumerate(unsortedlist):
            distance = getdistance(currenttrack.normalizedlist, track.normalizedlist)
            if distance < closesttrackdistance:
                closesttrackdistance = distance
                closesttrackindex = i

        # make that track currenttrack, pop off unsortedlist
        currenttrack = unsortedlist.pop(closesttrackindex)

        # append current track to sortedlist
        sortedlist.append(currenttrack)

    # append last track to list
    sortedlist.append(unsortedlist.pop())

    return(sortedlist)

def getdistance(vector1, vector2):
    """
        Accepts two vectors (track.normalizedlist arrays, containing weighted 
        values for each track attribute). Vectors must be the same length.

        Returns the distance between the two vectors, or None if there is an
        error.
    """
    try:
        result = math.sqrt(sum([math.pow(i - j, 2) for i, j in zip(vector1,
                                                            vector2)]))
        return(result)
    except Exception as e:
        print('error in getdistance:\n{}'.format(e))
        return(None)


