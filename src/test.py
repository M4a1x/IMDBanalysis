import os
import time
from extract import *

RATINGS_PATH = os.path.abspath('../database/selection/ratings.list')
GENRES_PATH = os.path.abspath('../database/selection/genres.list')
KEYWORDS_PATH = os.path.abspath('../database/selection/keywords.list')
LANGUAGES_PATH = os.path.abspath('../database/selection/language.list')
starttime = time.process_time()
GR = get_ratings(RATINGS_PATH)
grtime = time.process_time() - starttime
starttime = time.process_time()
GG = get_genres(GENRES_PATH)
ggtime = time.process_time() - starttime
starttime = time.process_time()
GK = get_keywords(KEYWORDS_PATH)
gktime = time.process_time() - starttime

starttime = time.process_time()
GL = get_languages(LANGUAGES_PATH)
gltime = time.process_time() -starttime

list1_dict = dict(GR)
list2_dict = dict(GG)
list3_dict = dict(GK)
    Create sets from the KEYS of the dicts and
    get a set which contains all entries from both ('&' operator).
    Then loop over the set and use entries as keys
    for the dicts to create the list
starttime = time.process_time()
combined =  [(id, list1_dict[id], list2_dict[id], list3_dict[id])
            for id in set(list1_dict) & set(list2_dict) & set(list3_dict)]
combinedtime = time.process_time() - starttime

from sys import getsizeof
print("Length of combined list: " + str(len(combined)))
print("Size of Combined: " + str(getsizeof(combined)) + " Took time: " + str(combinedtime))
print("Size of GR: " + str(getsizeof(GR)) + " Took time: " + str(grtime))
print("Size of GG: " + str(getsizeof(GG)) + " Took time: " + str(ggtime))
print("Size of GK: " + str(getsizeof(GK)) + " Took time: " + str(gktime))
print("Size of GL: " + str(getsizeof(GL)) + " Took time: " + str(gltime))
# TODO: Print number of elements in each list. 
# TODO: Check first and last element to make sure nothings is omitted