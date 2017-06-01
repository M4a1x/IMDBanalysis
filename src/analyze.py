import logging

log = logging.getLogger(__name__)


# Outdated
def get_ratings_sublist(ratings, restrict_votes):
    restricted_list = []
    for movie in ratings:
        if (int(movie[0]) >= restrict_votes):
            restricted_list.append(movie)
    return restricted_list


def get_common(movie_list1, movie_list2):
    # Make dictionaries out of the lists with the movie tuple being the key
    # e.g.:
    # {('Title', 'Year', ...): ('votes', 'ratings')}
    # {('Title', 'Year', ...): ['Genre1', 'Genre2']}
    list1_dict = dict(movie_list1)
    list2_dict = dict(movie_list2)
    # Create sets from the KEYS of the dicts and
    # get a set which contains all entries from both ('&' operator).
    # Then loop over the set and use entries as keys
    #  for the dicts to create the list
    return [(id, list1_dict[id], list2_dict[id])
            for id in (set(list1_dict) & set(list2_dict))]


# Outdated
def get_totals(ratings, restrict_votes=0):
    ratings_sum = 0
    votes_sum = 0
    movies_sum = 0
    log.info("Starting loop to summarize votes/ratings/number")
    for movie in ratings:
        votes = int(movie[0])
        if (votes >= restrict_votes):
            votes_sum += int(votes)
            ratings_sum += float(movie[1])
            movies_sum += 1
    return (movies_sum, votes_sum, ratings_sum)


# Outdated
def print_avg_tot(ratings, restrict_votes=0):
    log.info("Getting the totals first...")
    movies_sum, votes_sum, ratings_sum = get_totals(ratings, restrict_votes)
    log.info("Print out the averages and totals")
    print("Total number of movies with >={} votes: {}".format(
        restrict_votes, movies_sum))
    print("Total number of votes for movies with >={} votes: {}".format(
        restrict_votes, votes_sum))
    print("Average number of votes for movies with >={} votes: {}".format(
          restrict_votes, votes_sum / movies_sum))
    print("Average rating (>={} votes): {}".format(
        restrict_votes, ratings_sum / movies_sum))
