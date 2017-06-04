import os
import time
from sys import getsizeof
from extract import *

RATINGS_PATH = os.path.abspath('../database/selection/ratings.list')
GENRES_PATH = os.path.abspath('../database/selection/genres.list')
KEYWORDS_PATH = os.path.abspath('../database/selection/keywords.list')
LANGUAGES_PATH = os.path.abspath('../database/selection/language.list')


def test_extract_function(function, path):
    """Test the extract functions of the extract module.

       Print time, size, length, first and last element.
    """
    starttime = time.process_time()
    data = function(path)
    dattime = time.process_time() - starttime
    print("{}: Size: {}. Length: {}. Time: {}.".format(
        function.__name__, getsizeof(data), len(data), dattime))
    print("{}: First Element: {}".format(function.__name__, data[0]))
    print("{}: Last Element: {}".format(function.__name__, data[-1]))

#test_extract_function(get_genres, GENRES_PATH)
#test_extract_function(get_keywords, KEYWORDS_PATH)
test_extract_function(get_languages, LANGUAGES_PATH)
# test_extract_function(get_ratings, RATINGS_PATH)


# list1_dict = dict(GR)
# list2_dict = dict(GG)
# list3_dict = dict(GK)
# # Create sets from the KEYS of the dicts and
# # get a set which contains all entries from both ('&' operator).
# # Then loop over the set and use entries as keys
# # for the dicts to create the list
# starttime = time.process_time()
# combined =  [(id, list1_dict[id], list2_dict[id], list3_dict[id])
#             for id in set(list1_dict) & set(list2_dict) & set(list3_dict)]
# combinedtime = time.process_time() - starttime
