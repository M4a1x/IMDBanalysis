""" Provides methods to extract data from the imdb dataset """

import logging
import re

LOG = logging.getLogger(__name__)


def get_ratings(file):
    """Reads in the ratings.list from imdb interface dump

    Args:
        file (str): The path to the ratings.list file

    Returns:
        list: A list of movies tuples containing votes and ratings

        The movie tuples are structured in two sub-touples.
        The first one identifing the movie, the second containing
        votecount and ratings.

        Format:
        (('Title', 'Year', 'opt. counter for movies with the same name',
        'opt. episode name', 'opt. VG|TV|V tag'), (votecount, rating))

    """

    regex = re.compile(
        r"\s+\*?\s*[\*\.\d]{10}\s+"  # Distribution of Votes
        r"(\d+)"                     # (Number of votes)
        r"\s+"
        r"(\d?\d\.\d)"               # (Rating)
        r"\s+"
        r"(.*)"                      # (Title (Movie/Series))
        r"\s\("
        r"([\d\?]{4})"               # (Year)
        r"/?([XIVLMD]+)?\)"          # opt. (Nr. of movies with same title?)
        r"(?:\s\{([^{}]+)\})?"       # opt. name of episode
        r"(?:\s\((VG|TV|V)\))?")     # opt. VG|TV|V for videogame|tv|video
    ratings = []

    # Open up ratings
    LOG.debug("Opening ratings file...")
    with open(file, 'r') as input_file:
        # Read until the main part where all movie ratings start
        for line in input_file:
            if 'MOVIE RATINGS REPORT' in line:
                break

        # Skip empty line and header of the list
        next(input_file)
        next(input_file)

        LOG.debug("Reached beginning of movie list")
        # Go through each line in the file
        for line in input_file:
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
                line = next(input_file)
                if line[0] == '-':
                    LOG.debug("Reached end of movie list")
                    break
                else:
                    # Oh oh, a movie couldn't be parsed!
                    raise NotImplementedError(
                        "There's a movie that coudnt't be parsed! "
                        "I don't know what to do!\n"
                        "Error occured before this line: " + line)
    LOG.info("Finised parsing ratings")
    return ratings


def get_genres(file):
    """Reads in the genres.list file from imdb interface dump

    Args:
        file (str): Path to the genre.list file

    Returns:
        list : A list of touples of the movies.

        The movie tuples themselves are formatted as follows:
        (('Title', 'Year', 'opt. counter for movies with same name',
        'opt. Episode title', 'opt. TV|V|VG'),
        ['List', 'of', 'genres'])

        The first touple inside the movie touple identifies the entry exactly
        The list contairs all genres this movie belongs to

    """

    regex = re.compile(
        r"(.*)"                      # (Title (Movie/Series))
        r"\s\("
        r"([\d\?]{4})"               # (Year|????)
        r"/?([XIVLMD]+)?\)"          # opt. (Nr. of movies with same title?)
        r"(?:\s\{([^{}]+)\})?"       # optional (Title of Episode)
        r"(?:\s\{\{SUSPENDED\}\})?"  # optional suspended tag
        r"(?:\s\((VG|TV|V)\))?"      # optional TV|V tag for tv/video releases
        r"\s+"
        r"(.*)")                     # (Genre)
    genres = []

    # Open up ratings
    LOG.debug("Opening genres file...")
    with open(file, 'r') as input_file:
        for line in input_file:
            if 'THE GENRES LIST' in line:
                break
        next(input_file)
        next(input_file)

        for line in input_file:
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
    LOG.info("Finised parsing genres")
    return genres
