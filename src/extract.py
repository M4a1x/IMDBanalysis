import os
import re
import logging

log = logging.getLogger(__name__)


def get_ratings():
    """Reads in the ratings.list from imdb interface dump

    Returns:
        list: A list of movies tuples containing votes and ratings

        The movie tuples are structured in two sub-touples.
        The first one identifing the movie, the second containing
        votecount and ratings.

        Format:
        (('Title', 'Year', 'opt. counter for movies with the same name',
        'opt. episode name', 'opt. VG|TV|V tag'), (votecount, rating))

    """
    # Input File: ratings.list
    filedir = os.path.join('..', 'database', 'selection')
    file = os.path.join(filedir, 'ratings.list')
    regex = re.compile(
        "\s+\*?\s*[\*\.\d]{10}\s+"  # Distribution of Votes
        "(\d+)"                     # (Number of votes)
        "\s+"
        "(\d?\d\.\d)"               # (Rating)
        "\s+"
        "(.*)"                      # (Title (Movie/Series))
        "\s\("
        "([\d\?]{4})"               # (Year)
        "/?([XIVLMD]+)?\)"          # opt. (Nr. of movies with same title?)
        "(?:\s\{([^{}]+)\})?"       # opt. name of episode
        "(?:\s\((VG|TV|V)\))?")     # opt. VG|TV|V for videogame|tv|video
    ratings = []

    # Open up ratings
    log.debug("Opening ratings file...")
    with open(file, 'r') as inF:
        # Read until the main part where all movie ratings start
        for line in inF:
            if 'MOVIE RATINGS REPORT' in line:
                break

        # Skip empty line and header of the list
        next(inF)
        next(inF)

        log.debug("Reached beginning of movie list")
        # Go through each line in the file
        for line in inF:
            # The regex parsing.
            # Returns a match which groups are formatted as follows:
            # (votes, rating, title, year|????, nr, title of episode, v|vg|tv)
            match = regex.match(line)
            if match:
                # Format it, first tuple is movie characteristics,
                # second touple is votecount and score
                element = (match.groups()[2:], match.groups()[:2])
                ratings.append(element)
            else:
                # If the long line with '----' is reached, the list is over
                line = next(inF)
                if line[0] == '-':
                    log.debug("Reached end of movie list")
                    break
                else:
                    # Oh oh, a movie couldn't be parsed!
                    raise NotImplementedError(
                        "There's a movie that coudnt't be parsed! "
                        "I don't know what to do!\n"
                        "Error occured before this line: " + line)
    log.info("Finised parsing ratings")
    return ratings


def get_genres():
    """Reads in the genres.list file from imdb interface dump

    Returns:
        list : A list of touples of the movies.

        The movie tuples themselves are formatted as follows:
        (('Title', 'Year', 'opt. counter for movies with same name',
        'opt. Episode title', 'opt. TV|V|VG'),
        ['List', 'of', 'genres'])

        The first touple inside the movie touple identifies the entry exactly
        The list contairs all genres this movie belongs to

    """
    # Input File: genres.list
    filedir = os.path.join('..', 'database', 'selection')
    file = os.path.join(filedir, 'genres.list')
    regex = re.compile(
        "(.*)"                      # (Title (Movie/Series))
        "\s\("
        "([\d\?]{4})"               # (Year|????)
        "/?([XIVLMD]+)?\)"          # opt. (Nr. of movies with same title?)
        "(?:\s\{([^{}]+)\})?"       # optional (Title of Episode)
        "(?:\s\{\{SUSPENDED\}\})?"  # optional suspended tag
        "(?:\s\((VG|TV|V)\))?"      # optional TV|V tag for tv/video releases
        "\s+"
        "(.*)")                     # (Genre)
    genres = []

    # Open up ratings
    log.debug("Opening genres file...")
    with open(file, 'r') as inF:
        for line in inF:
            if 'THE GENRES LIST' in line:
                break
        print(next(inF))
        print(next(inF))

        for line in inF:
            match = regex.match(line)
            if match:
                tpl = match.groups()
                # Assuming that entries for the same movie are grouped together
                # Formating a little
                if genres and genres[-1][0] == tpl[:5]:
                    # Add genres to existings movies
                    genres[-1][1].append(tpl[5])
                else:
                    # Or create new entry if movie does not exist
                    element = (tpl[:5], [tpl[5]])
                    genres.append(element)
            else:
                # Oh oh, a movie couldn't be parsed!
                raise NotImplementedError(
                    "There's a movie that coudnt't be parsed! "
                    "I don't know what to do!\n"
                    "Error occured before this line: " + line)
    log.info("Finised parsing genres")
    return genres
