""" Provides methods to extract data from the imdb dataset """
import logging
import re
import pickle
import os
import gzip  # Because SPEED is priority here.
import urllib.request
from collections import namedtuple
LOG = logging.getLogger(__name__)

# TODO: Change open() operations to directly act on .list.gz files instead of .list files
# TODO: Change combine function to reduce memory usage
# TODO: Implement missing functions

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

TECH_DICT = {k: v for v, k in enumerate(Tech._fields)}


Business = namedtuple('Business', ['bt', 'gr', 'ow', 'rt',
                                   'ad', 'sd', 'pd', 'st', 'cp', 'wg'])
Business.__doc__ += ": Container for business and economic data about a movie"
Business.bt.__doc__ = "Budget"
Business.gr.__doc__ = "Box Office Gross"
Business.ow.__doc__ = "Opening Weekends Box Office Gross"
Business.rt.__doc__ = "Rentals (money that goes back to the distributor)"
Business.ad.__doc__ = "Admissions (# of Tickets sold"
Business.sd.__doc__ = "Shootings Dates"
Business.pd.__doc__ = "Production Dates"
Business.st.__doc__ = "Studio where the movie was filmed"
Business.cp.__doc__ = "Copyright Holder"
Business.wg.__doc__ = "Weekend Gross"

BUSINESS_DICT = {k: v for v, k in enumerate(Business._fields)}


MOVIE_PATTERN = (
    r"(.*)"                       # (Title (Movie/Series))
    r"\s\("
    r"([\d\?]{4})"                # (Year|????)
    r"/?([XIVLMD]+)?\)"           # opt. (Nr. of movies with same title?)
    r"(?:\s\{([^{}]+)\})?"        # optional (Title of Episode)
    r"(?:\s\((VG|TV|V)\))?"       # optional TV|V tag for tv/video releases
    r"(?:\s\{\{SUSPENDED\}\})?")  # optional suspended tag

BASE_URL = "ftp://ftp.fu-berlin.de/pub/misc/movies/database/"  # Default URL
FILE_LIST = ('ratings', 'genres', 'keywords', 'language',
             'locations', 'running_times', 'technical', 'business')


def get_matches(file: str, regex: str,
                start: str, skip: int):
    """Reads in a *.list file from imdb interface dump and performs regex
       on every line

    Args:
        file: The path to the *.list file
        regex: The regex pattern that matches the whole line
        start: Indicates the start of the
               main list (skip preceeding comments/metadata)
        skip: Number of lines to skip after 'start'
              to reach the beginning of the main list

    Returns:
        Generator of tuples: [(Data1), (Data2), ...]
    """

    # Open up *.list file
    LOG.debug("Opening list file %s...", file)
    with open(file, 'r') as input_file:
        # Skip all lines until the start str (skip comments/meta)
        for line in input_file:
            if start in line:
                break
        # Skip 'skip' nr of lines to main body
        for _ in range(skip):
            next(input_file)

        # Read in main data
        for line in input_file:
            match = re.match(regex, line)
            if match:
                yield match.groups()
            else:
                # If the long stop line is reached, the main list is over
                # Skip possible empty lines
                while line == '\n':
                    line = next(input_file)
                if '-------------------------------------------------' in line:
                    LOG.debug("Reached end of list %s", file)
                    break
                else:
                    # It's no the stopline! A movie couldn't be parsed!
                    raise NotImplementedError(
                        "There's a movie that coudnt't be parsed! "
                        "I don't know what to do!\n"
                        "Error occured on this line: " + line)
    # Will finish without error if file just reaches eof
    LOG.info("Finised parsing list %s", file)


def get_movie_matches(file: str, data_regex: str,
                      start: str, skip: int):
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

    Returns:
        Generator of tuples of type: (Movie, [Data])
    """

    pattern = MOVIE_PATTERN + r"\s+" + data_regex

    LOG.debug("Start parsing the regexed lines from %s", file)

    entry = ()
    for line in get_matches(file, pattern, start, skip):
        mov = Movie(line[0], int(line[1]) if line[1] != '????' else None,
                    *line[2:5])
        if not entry:
            entry = (mov, [line[5]])
        elif mov == entry[0]:
            entry[1].append(line[5])
        else:
            yield entry
            entry = (mov, [line[5]])
    yield entry  # Yield the last entry

    LOG.info("Finised parsing movie type list %s", file)


def get_ratings(file: str):
    """Reads in the ratings.list from imdb interface dump

    Args:
        file: The path to the ratings.list file

    Returns:
        Generator of tuples: (Movie, (votes, ratings))
    """

    ratings_pattern = (
        r"\s+\*?\s*[\*\.\d]{10}\s+"  # Distribution of Votes
        r"(\d+)"                     # (Number of votes)
        r"\s+"
        r"(\d?\d\.\d)")              # (Rating)

    pattern = ratings_pattern + r"\s+" + MOVIE_PATTERN
    start = 'MOVIE RATINGS REPORT'
    skip = 2

    LOG.debug("Parsing ratings...")
    for line in get_matches(file, pattern, start, skip):
        mov = Movie(line[2], int(line[3]) if line[3] != '????' else None,
                    *line[4:7])
        element = (mov, (int(line[0]), float(line[1])))
        yield element

    LOG.info("Finised parsing ratings list")


def get_genres(file: str):
    """Reads in the genres.list file from imdb interface dump

    Args:
        file: The path to the genres.list file

    Returns:
        Generator of tuples of type: (Movie, ['list', 'of', 'genres'])
    """

    LOG.debug("Parsing genres...")
    pattern = r"(.*)"  # (Keywords)
    start = 'THE GENRES LIST'
    skip = 2

    for entry in get_movie_matches(file, pattern, start, skip):
        yield entry
    LOG.debug("Finished parsing genres...")


def get_keywords(file: str):
    """Reads in the keywords.list file from imdb interface dump

    Args:
        file: The path to the keywords.list file

    Returns:
        Generator of tuples ot type: (Movie, ['list', 'of', 'keywords'])
    """
    LOG.debug("Parsing keywords...")

    pattern = r"(.*)"  # (Keywords)
    start = 'THE KEYWORDS LIST'
    skip = 2

    for entry in get_movie_matches(file, pattern, start, skip):
        yield entry

    LOG.debug("Finished parsing keywords")


def get_languages(file: str):
    """Reads in the language.list file from imdb interface dump

    Args:
        file: The path to the language.list file

    Returns:
        Generator of tuples of type: (Movie, ["Language"])
    """
    LOG.debug("Parsing languages...")

    pattern = (r"(.*)"                      # (Languages)
               r"(?:\s+.*)?")               # opt. additional info
    start = 'LANGUAGE LIST'
    skip = 1

    for entry in get_movie_matches(file, pattern, start, skip):
        yield entry

    LOG.debug("Finished parsing languages")


def get_locations(file: str):
    """Reads in the locations.list file from the imdb interface dump

    Args:
        file: path to the file

    Returns:
        Generator of tuples of type (Movie, ["Location A", "Location B", ...])
    """
    LOG.debug("Parsing locations...")

    pattern = r"\(?([^(\n\t]+)\)?(?:\s*\(.*\))?"
    start = 'LOCATIONS LIST'
    skip = 1

    for entry in get_movie_matches(file, pattern, start, skip):
        yield entry

    LOG.debug("Finihed parsing locations")


def get_running_times(file: str):
    """Reads in the running-times.list file from the imdb interface dump

    Args:
        file: path to the file

    Returns:
        Generator of tuples of type (Movie, [Time in Minutes])
    """
    LOG.debug("Parsing running-times...")

    pattern = r"[^\d]*(\d+)"
    start = 'RUNNING TIMES LIST'
    skip = 1

    for entry in get_movie_matches(file, pattern, start, skip):
        yield entry

    LOG.debug("Finished parsing running-times")


def get_technicals(file: str):
    """Reads in the technical.list

    Args:
        file: path to the file

    Returns:
        Generator of tuples of type (Movie, Tech)
    """
    LOG.debug("Parsing technicals...")

    pattern = (MOVIE_PATTERN + r"\s+" +
               r"(CAM|MET|OFM|PFM|RAT|PCS|LAB):([^(\t\n/]*)")
    start = 'TECHNICAL LIST'
    skip = 3

    entry = ()
    for line in get_matches(file, pattern, start, skip):
        mov = Movie(line[0], int(line[1]) if line[1] != '????' else None,
                    *line[2:5])
        index = TECH_DICT[line[5].lower()]
        # Remove trailing space.. there's probably a better way
        data = line[6][:-1] if line[6][:-1] == ' ' else line[6]

        if not entry:  # Only first iteration. Create new entry
            tec = Tech(*[[] for _ in Tech._fields])
            tec[index].append(data)
            entry = (mov, tec)
        elif entry[0] == mov:  # Current line is from same movie as last => add
            entry[1][index].append(data)
        else:  # curr. line is dif. mov. => yield and create new entry
            yield entry
            tec = Tech(*[[] for _ in Tech._fields])
            tec[index].append(data)
            entry = (mov, tec)
    yield entry

    LOG.debug("Finished parsing technicals")


def get_businesses(file: str):
    """ Get business information from business.list

    Args:
        file: The path to the file

    Returns:
        Generator of tuples of type (Movie, Business)
    """
    LOG.debug("Parsing businesses...")

    pattern = r"(BT|GR|OW|RT|AD|SD|PD|ST|CP|WG):\s(.*)"

    LOG.debug("Opening list file...")
    with open(file, 'r') as input_file:
        # Skip all lines until the start str (skip comments/meta)
        for line in input_file:
            if line == 'BUSINESS LIST\n':
                break
        # Skip 'skip' lines to main body
        for _ in range(2):
            next(input_file)

        for line in input_file:  # Loop over movie entries
            if line == '\n':
                continue
            if '-----------------------------------------------------' in line:
                break
            bsns = Business(*[[] for _ in Business._fields])
            title = re.match(MOVIE_PATTERN,
                             line[4:]).groups()  # First line always MV
            mov = Movie(title[0],
                        int(title[1]) if title[1] != '????' else None,
                        *title[2:5])

            for entry in input_file:  # Looping over the entry of one movie
                if entry == '\n':
                    continue
                if '------------------------------------------------' in entry:
                    break
                result = re.match(pattern, entry).groups()
                index = BUSINESS_DICT[result[0].lower()]  # Get index of field
                bsns[index].append(result[1])             # in the named tuple

            yield (mov, bsns)

    LOG.debug("Finished parsing businesses")


def get_directors(file: str) -> list:
    """Not important.?"""
    pass


def get_movie_links(file: str) -> list:
    """No time I guess."""
    pass


def get_actors(file: str) -> list:
    """Very large list, maybe later.."""
    pass


def get_actresses(file: str) -> list:
    """Also very large list, maybe later.."""
    pass


def combine_lists(*lists) -> list:
    """Combine the provided lists into one file. Drops all not shared entries.

    Args:
        lists: The lists to combine

    Returns:
        Combined list
    """
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


def combine_generator(*generators):
    """ Combines the data from the given generators into one list

    This helps especially with large datasets or lots of sets, to reduce
    memory usage.

    Args:
        generator functions to get the data

    Returns:
        Dictionary of combined movies. {mov: [gen1_data, gen2_data, ...]}
    """
    curr_list = [x for x in generators[0]]
    curr_dict = dict(curr_list)
    curr_set = set(curr_dict)

    return_dict = {k: [v] for k, v in curr_dict.items()}

    for generator in generators[1:]:
        this_list = [elem for elem in generator]
        this_dict = dict(this_list)
        this_set = set(this_dict)

        curr_set = curr_set & this_set
        diff_set = curr_set - this_set

        for iden in diff_set:
            return_dict.pop(iden)

        for iden in curr_set:
            return_dict[iden].append(this_dict[iden])

    return return_dict


def download_data(directory: str, url: str=BASE_URL,
                  files: tuple=FILE_LIST) -> None:
    """Download the specified list files from the imdb database

    Args:
        directory: The directory to save the files in. Must exist
        url: The url to download from. Default is berlin mirror
        files: A tuple of filenames to download (e.g. genres, ratings, ...)
    """
    if not os.path.exists(directory):
        raise IOError("This path doesn't exist!")

    if not os.path.isdir(directory):
        raise IOError("This is not a directory!")

    LOG.info("Starting download...")
    for file in files:
        path = os.path.join(directory, file + '.list.gz')
        url_full = url + file + '.list.gz'
        if os.path.exists(path):
            raise IOError("File already exists!")
        urllib.request.urlretrieve(url_full, path)
        LOG.info("Finised downloading " + path)


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
