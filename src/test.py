import os
import time
from sys import getsizeof
from extract import *

logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.abspath('../database/selection/')
PICKLE_PATH = os.path.abspath('../database/pickle/')
RATINGS_PATH = os.path.abspath('../database/selection/ratings.list')
GENRES_PATH = os.path.abspath('../database/selection/genres.list')
KEYWORDS_PATH = os.path.abspath('../database/selection/keywords.list')
LANGUAGES_PATH = os.path.abspath('../database/selection/language.list')
LOCATIONS_PATH = os.path.join(BASE_PATH, 'locations.list')
RUNNING_TIMES_PATH = os.path.join(BASE_PATH, 'running-times.list')
TECHNICALS_PATH = os.path.join(BASE_PATH, 'technical.list')
BUSINESSES_PATH = os.path.join(BASE_PATH, 'business.list')

def test_extract_function(function, arg):
    """Test the extract functions of the extract module.

       Print time, size, length, first and last element.
    """

    full_data = []
    starttime = time.process_time()
    if isinstance(arg, str):
        data = function(arg)
    else:
        data = function(*arg)

    for x in data:
        full_data.append(x)
    dattime = time.process_time() - starttime

    print("{}: Size: {}. Length: {}. Time: {}.".format(
        function.__name__, getsizeof(full_data), len(full_data), dattime))
    print("{}: First Element: {}".format(function.__name__, full_data[0]))
    print("{}: Last Element: {}".format(function.__name__, full_data[-1]))
    return data

gg = test_extract_function(get_genres, GENRES_PATH)
gk = test_extract_function(get_keywords, KEYWORDS_PATH)
glang =  test_extract_function(get_languages, LANGUAGES_PATH)
grat =  test_extract_function(get_ratings, RATINGS_PATH)
gloc = test_extract_function(get_locations, LOCATIONS_PATH)
grun = test_extract_function(get_running_times, RUNNING_TIMES_PATH)
gt = test_extract_function(get_technicals, TECHNICALS_PATH)
gb = test_extract_function(get_businesses, BUSINESSES_PATH)
# combine = test_extract_function(combine_lists, (gg, gk, gl, gr))

starttime = time.process_time()
save(PICKLE_PATH, genres=gg, keywords=gk, language=glang, ratings=grat, locations=gloc, running_times=grun, technical=gt)
gg, gk, glang, grat, gloc, grun, gt = load(PICKLE_PATH, "genres", "keywords", "language", "ratings", "locations", "running_times", "technical")
dattime = time.process_time() - starttime

# TODO: Make this more memory efficient: Combine only the first two, get third, combine, get forth, combine, etc...
combine = test_extract_function(combine_lists, (gg, gk, glang, grat, gloc, grun, gt))

download_data(BASE_PATH)