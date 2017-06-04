""" Provides methods to extract data from the imdb dataset """
import logging
import re
from collections import namedtuple
LOG = logging.getLogger(__name__)

Movie = namedtuple('Movie', ['title', 'year', 'counter', 'episode', 'tag'])
Movie.__doc__ += ": Container for movie identification data."
Movie.title.__doc__ = "Title of the movie/tv series/game/video/..."
Movie.year.__doc__ = "Year the movie was released"
Movie.counter.__doc__ = "Counter for movies with the same name"
Movie.episode.__doc__ = "Title of the episode"
Movie.tag.__doc__ = """VG|TV|V 
                       indicating videogame, tv release, video respectively"""


def get_ratings(file: str) -> list:
    """Reads in the ratings.list from imdb interface dump

    Args:
        file: The path to the ratings.list file

    Returns:
        A list of tuples: (Movie, (votes, ratings))
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
    ratings = []  # type: list

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
                # Format it, first entry is movie characteristics,
                # touple is votecount and score
                grps = match.groups()
                mov = Movie(grps[2],
                            int(grps[3]) if grps[3] != '????' else None,
                            *grps[4:7])
                element = (mov,
                           (int(match.groups()[0]), float(match.groups()[1])))
                ratings.append(element)
            else:
                # If the long line with '----' is reached, the list is over
                line = next(input_file)
                if line[0] == '-':
                    LOG.debug("Reached end of ratings list")
                    break
                else:
                    # Oh oh, a movie couldn't be parsed!
                    raise NotImplementedError(
                        "There's a movie that coudnt't be parsed! "
                        "I don't know what to do!\n"
                        "Error occured before this line: " + line)
    LOG.info("Finised parsing ratings")
    return ratings


def get_genres(file: str) -> list:
    """Reads in the genres.list file from imdb interface dump

    Args:
        file: The path to the genres.list file

    Returns:
        A list of tuples: (Movie, ['list', 'of', 'genres'])
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
    genres = []  # type: list

    # Open up ratings
    LOG.debug("Opening genres file...")
    with open(file, 'r') as input_file:
        # Skip all lines until the main list starts
        for line in input_file:
            if 'THE GENRES LIST' in line:
                break
        next(input_file)
        next(input_file)

        for line in input_file:
            match = regex.match(line)
            if match:
                tpl = match.groups()
                mov = Movie(tpl[0], int(tpl[1]) if tpl[1] != '????' else None,
                            *tpl[2:5])
                # Assuming that entries for the same movie are grouped together
                # If last movie is the same as the current one
                if genres and genres[-1][0] == mov:
                    # Add current genre to existings movies
                    genres[-1][1].append(tpl[5])
                else:
                    # Or create new entry if movie does not exist
                    element = (mov, [tpl[5]])
                    genres.append(element)
            else:
                # Oh oh, a movie couldn't be parsed!
                raise NotImplementedError(
                    "There's a movie that coudnt't be parsed! "
                    "I don't know what to do!\n"
                    "Error occured before this line: " + line)
    LOG.info("Finised parsing genres")
    return genres


def get_keywords(file: str) -> list:
    """Reads in the keywords.list file from imdb interface dump

    Args:
        file: The path to the keywords.list file

    Returns:
        A list of tuples: (Movie, ['list', 'of', 'keywords'])
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
    keywords = []  # type: list

    # Open up ratings
    LOG.debug("Opening keywords file...")
    with open(file, 'r') as input_file:
        # Skip all lines until the main list starts
        for line in input_file:
            if 'THE KEYWORDS LIST' in line:
                break
        next(input_file)
        next(input_file)

        for line in input_file:
            match = regex.match(line)
            if match:
                tpl = match.groups()
                mov = Movie(tpl[0], int(tpl[1]) if tpl[1] != '????' else None,
                            *tpl[2:5])
                # Assuming that entries for the same movie are grouped together
                # If last movie is the same as the current one
                if keywords and keywords[-1][0] == mov:
                    # Add current keyword to existing movie
                    keywords[-1][1].append(tpl[5])
                else:
                    # Or create new entry if movie does not exist
                    element = (mov, [tpl[5]])
                    keywords.append(element)
            else:
                # Oh oh, a movie couldn't be parsed!
                raise NotImplementedError(
                    "There's a movie that coudnt't be parsed! "
                    "I don't know what to do!\n"
                    "Error occured before this line: " + line)
    LOG.info("Finised parsing keywords")
    return keywords


def get_languages(file: str) -> list:
    """Reads in the language.list file from imdb interface dump

    Args:
        file: The path to the language.list file

    Returns:
        A list of tuples: (Movie, "Language")
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
        r"(.*)"                      # (Languages)
        r"(?:\s+.*)?")               # opt. additional info
    languages = []  # type: list

    # Open up ratings
    LOG.debug("Opening languages file...")
    with open(file, 'r') as input_file:
        # Skip all lines until the main list starts
        for line in input_file:
            if 'LANGUAGE LIST' in line:
                break
        next(input_file)

        for line in input_file:
            match = regex.match(line)
            if match:
                tpl = match.groups()
                mov = Movie(tpl[0], int(tpl[1]) if tpl[1] != '????' else None,
                            *tpl[2:5])
                # Assuming that entries for the same movie are grouped together
                # If last movie is the same as the current one
                if languages and languages[-1][0] == mov:
                    # Add current language to existing movie
                    languages[-1][1].append(tpl[5])
                else:
                    # Or create new entry if movie does not exist
                    element = (mov, [tpl[5]])
                    languages.append(element)
            else:
                # If the long line with '----' is reached, the list is over
                if line[0] == '-':
                    LOG.debug("Reached end of language list")
                    break
                else:
                    # Oh oh, a movie couldn't be parsed!
                    raise NotImplementedError(
                        "There's a movie that coudnt't be parsed! "
                        "I don't know what to do!\n"
                        "Error occured before this line: " + line)
    LOG.info("Finised parsing languages")
    return languages

# --------------------------------IF EXECUTED-------------------------------- #
if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import os
    import time
    RATINGS_PATH = os.path.abspath('../database/selection/ratings.list')
    GENRES_PATH = os.path.abspath('../database/selection/genres.list')
    KEYWORDS_PATH = os.path.abspath('../database/selection/keywords.list')
    LANGUAGES_PATH = os.path.abspath('../database/selection/language.list')
    # starttime = time.process_time()
    # GR = get_ratings(RATINGS_PATH)
    # grtime = time.process_time() - starttime
    # starttime = time.process_time()
    # GG = get_genres(GENRES_PATH)
    # ggtime = time.process_time() - starttime
    # starttime = time.process_time()
    # GK = get_keywords(KEYWORDS_PATH)
    # gktime = time.process_time() - starttime

    starttime = time.process_time()
    GL = get_languages(LANGUAGES_PATH)
    gltime = time.process_time() -starttime

    #list1_dict = dict(GR)
    #list2_dict = dict(GG)
    #list3_dict = dict(GK)
    # Create sets from the KEYS of the dicts and
    # get a set which contains all entries from both ('&' operator).
    # Then loop over the set and use entries as keys
    #  for the dicts to create the list
    #starttime = time.process_time()
    #combined =  [(id, list1_dict[id], list2_dict[id], list3_dict[id])
    #            for id in set(list1_dict) & set(list2_dict) & set(list3_dict)]
    #combinedtime = time.process_time() - starttime
    
    #from sys import getsizeof
    #print("Length of combined list: " + str(len(combined)))
    #print("Size of Combined: " + str(getsizeof(combined)) + " Took time: " + str(combinedtime))
    #print("Size of GR: " + str(getsizeof(GR)) + " Took time: " + str(grtime))
    #print("Size of GG: " + str(getsizeof(GG)) + " Took time: " + str(ggtime))
    #print("Size of GK: " + str(getsizeof(GK)) + " Took time: " + str(gktime))
    print(GL[0])
    print(len(GL))
    print(GL[-1])
    print(gltime)
