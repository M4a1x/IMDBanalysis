""" Provides methods to extract data from the imdb dataset """
import logging
import re
import pickle
import os
import gzip  # Because SPEED is priority here.
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

Tech = namedtuple('Tech', ['cam', 'met', 'ofm', 'pfm', 'rat', 'pcs', 'lab'])
Tech.__doc__ += ": Container for technicals.list information of a movie"
Tech.cam.__doc__ = "Camera model and Lens information"
Tech.met.__doc__ = "Length of a film in meter"
Tech.ofm.__doc__ = ("Film negative format in mm or 'Video' with an additional"
                    "attribute for the TV standard")
Tech.pfm.__doc__ = ("Printed film format in mm or 'Video' with an additional"
                    "attribute for the TV standard")
Tech.rat.__doc__ = "Aspect Ratio, width to height (_.__ : 1)"
Tech.pcs.__doc__ = "Cinematographic process or video system"
Tech.lab.__doc__ = "Laboratory (Syntax: Laboratory name, Location, Country)"

MOVIE_PATTERN = (
    r"(.*)"                      # (Title (Movie/Series))
    r"\s\("
    r"([\d\?]{4})"               # (Year|????)
    r"/?([XIVLMD]+)?\)"          # opt. (Nr. of movies with same title?)
    r"(?:\s\{([^{}]+)\})?"       # optional (Title of Episode)
    r"(?:\s\{\{SUSPENDED\}\})?"  # optional suspended tag
    r"(?:\s\((VG|TV|V)\))?")     # optional TV|V tag for tv/video releases


def get_matches(file: str, regex: str,
                start: str, skip: int, stop: str) -> list:
    """Reads in a *.list file from imdb interface dump and performs regex
       on every line

    Args:
        file: The path to the *.list file
        regex: The regex pattern that matches the whole line
        start: Indicates the start of the
               main list (skip preceeding comments/metadata)
        skip: Number of lines to skip after 'start'
              to reach the beginning of the main list
        stop: Indicates the stop of the main list (omit trailing comments/meta)

    Returns:
        A list of tuples: [(Data1), (Data2), ...]
    """

    return_list = []  # type: list

    # Open up *.list file
    LOG.debug("Opening list file...")
    with open(file, 'r') as input_file:
        # Skip all lines until the start str (skip comments/meta)
        for line in input_file:
            if start in line:
                break
        # Skip 'skip' lines to main body
        for _ in range(skip):
            next(input_file)

        # Read in main data
        for line in input_file:
            match = re.match(regex, line)
            if match:
                return_list.append(match.groups())
            else:
                # If the long stop line is reached, the main list is over
                # Skip possible empty lines
                while line == '\n':
                    line = next(input_file)
                if stop in line:
                    LOG.debug("Reached end of list")
                    break
                else:
                    # It's no the stopline! A movie couldn't be parsed!
                    raise NotImplementedError(
                        "There's a movie that coudnt't be parsed! "
                        "I don't know what to do!\n"
                        "Error occured on this line: " + line)
    LOG.info("Finised parsing list")
    return return_list


def get_movie_matches(file: str, data_regex: str,
                      start: str, skip: int, stop: str) -> list:
    """Reads in a *.list file from imdb interface dump and performs regex

    This method provides a unified way to read in the *.list files which are in
    the 'Movie \s+ Data' format.

    Args:
        file: The path to the *.list file

        regex: The regex pattern that matches the specific end of the line
               aka. only the data. It must contain one group

        start: Indicates the start of the
               main list (skip preceeding comments/metadata)

        skip: Number of lines to skip after 'start'
              to reach the beginning of the main list

        stop: Indicates the stop of the main list (omit trailing comments/meta)

    Returns:
        A list of tuples of type: (Movie, [Data])
    """

    movie_list = []  # type: list
    pattern = MOVIE_PATTERN + r"\s+" + data_regex

    for line in get_matches(file, pattern, start, skip, stop):
        mov = Movie(line[0], int(line[1]) if line[1] != '????' else None,
                    *line[2:5])
        # Assuming that entries for the same movie are grouped together
        # If last movie is the same as the current one
        if movie_list and movie_list[-1][0] == mov:
            # Add current data to existing movie
            movie_list[-1][1].append(line[5])
        else:
            # Or create new entry if movie does not exist
            entry = (mov, [line[5]])
            movie_list.append(entry)

    LOG.info("Finised parsing movie type list")
    return movie_list


def get_ratings(file: str) -> list:
    """Reads in the ratings.list from imdb interface dump

    Args:
        file: The path to the ratings.list file

    Returns:
        A list of tuples: (Movie, (votes, ratings))
    """

    ratings_pattern = (
        r"\s+\*?\s*[\*\.\d]{10}\s+"  # Distribution of Votes
        r"(\d+)"                     # (Number of votes)
        r"\s+"
        r"(\d?\d\.\d)")              # (Rating)

    ratings = []  # type: list

    pattern = ratings_pattern + r"\s+" + MOVIE_PATTERN
    start = 'MOVIE RATINGS REPORT'
    skip = 2
    stop = '------------------------------------------------------------------'

    for line in get_matches(file, pattern, start, skip, stop):
        mov = Movie(line[2], int(line[3]) if line[3] != '????' else None,
                    *line[4:7])
        element = (mov, (int(line[0]), float(line[1])))
        ratings.append(element)

    LOG.info("Finised parsing ratings list")
    return ratings


def get_genres(file: str) -> list:
    """Reads in the genres.list file from imdb interface dump

    Args:
        file: The path to the genres.list file

    Returns:
        A list of tuples of type: (Movie, ['list', 'of', 'genres'])
    """

    pattern = r"(.*)"  # (Keywords)
    start = 'THE GENRES LIST'
    skip = 2
    stop = ''  # End of list equals end of file

    return get_movie_matches(file, pattern, start, skip, stop)


def get_keywords(file: str) -> list:
    """Reads in the keywords.list file from imdb interface dump

    Args:
        file: The path to the keywords.list file

    Returns:
        A list of tuples ot type: (Movie, ['list', 'of', 'keywords'])
    """

    pattern = r"(.*)"  # (Keywords)
    start = 'THE KEYWORDS LIST'
    skip = 2
    stop = ''  # End of list equals end of file

    return get_movie_matches(file, pattern, start, skip, stop)


def get_languages(file: str) -> list:
    """Reads in the language.list file from imdb interface dump

    Args:
        file: The path to the language.list file

    Returns:
        A list of tuples of type: (Movie, ["Language"])
    """

    pattern = (r"(.*)"                      # (Languages)
               r"(?:\s+.*)?")               # opt. additional info
    start = 'LANGUAGE LIST'
    skip = 1
    stop = '------------------------------------------------------------------'

    return get_movie_matches(file, pattern, start, skip, stop)


def get_locations(file: str) -> list:
    """Reads in the locations.list file from the imdb interface dump

    Args:
        file: path to the file

    Returns:
        A list of tuples of type (Movie, ["Location A", "Location B", ...])
    """

    pattern = r"\(?([^(\n\t]+)\)?(?:\s*\(.*\))?"
    start = 'LOCATIONS LIST'
    skip = 1
    stop = '------------------------------------------------------------------'

    return get_movie_matches(file, pattern, start, skip, stop)


def get_running_times(file: str) -> list:
    """Reads in the running-times.list file from the imdb interface dump

    Args:
        file: path to the file

    Returns:
        A list of tuples of type (Movie, [Time in Minutes])
    """
    pattern = r"[^\d]*(\d+)"
    start = 'RUNNING TIMES LIST'
    skip = 1
    stop = '------------------------------------------------------------------'
    return get_movie_matches(file, pattern, start, skip, stop)


def get_technicals(file: str) -> list:
    """Reads in the technical.list

    Args:
        file: path to the file

    Returns:
        A list of tuples of type (Movie, Tech)
    Maybe this is not useful..."""
    pass


def get_businesses(file: str) -> list:
    pass


def get_directors(file: str) -> list:
    pass


def get_actors(file: str) -> list:
    """Very large list, maybe later.."""
    pass


def get_actresses(file: str) -> list:
    """Also very large list, maybe later.."""
    pass


def combine_lists(*lists) -> list:
    dict_lists = []
    set_lists = []
    for index in range(len(lists)):
        dict_lists.append(dict(lists[index]))
        set_lists.append(set(dict_lists[index]))

    combined_set = set_lists[0]
    for index in range(1, len(set_lists)):
        combined_set = combined_set & set_lists[index]

    return_list = []
    for iden in combined_set:
        combined_entry = [iden]
        for dct in dict_lists:
            combined_entry.append(dct[iden])
        return_list.append(combined_entry)

    return return_list


def save(directory: str, **lists) -> None:
    """Dump the imdb extracted lists as pickle objects to disk

    Data can be restored with the "load()" function
    Args:
        directory: The directory to store the list dumps in
        *lists: The lists to be saved, key is the filename for the given list
    """
    if not os.path.isdir(directory):
        raise IOError("Specified directory {} doesn't exist".format(directory))

    for filename, imdblist in lists.items():
        filepath = os.path.join(directory, filename + '.pickle.gz')
        with gzip.open(filepath, 'wb') as output_file:
            pickle.dump(imdblist, output_file, pickle.HIGHEST_PROTOCOL)


def load(directory: str, *lists) -> list:
    """Load the pickled lists back into memory

    Data can be saved with the "save()" function
    Args:
        directory: The directory which contains the files
        lists: A str list of filenames to load
    """
    if not os.path.isdir(directory):
        raise IOError("Specified directory {} doesn't exist".format(directory))

    imdblists = []
    for filename in lists:
        filepath = os.path.join(directory, filename + '.pickle.gz')
        if not os.path.isfile(filepath):
            IOError("File {} doesn't exist".format(filepath))
        with gzip.open(filepath, 'rb') as input_file:
            imdblists.append(pickle.load(input_file))
    return imdblists


# --------------------------------IF EXECUTED-------------------------------- #
if __name__ == '__main__':
    import doctest
    doctest.testmod()
