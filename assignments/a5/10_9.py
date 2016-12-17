import os
import pickle
import random

import recommendations as r

if __name__ == '__main__':
    _, _, prefs = pickle.load(open('movielens.pkl'))

    # To make item-based, transform prefs, so the format of prefs will be prefs[movie][user] = rating
    prefs = r.transform_prefs(prefs)

    # Split prefs into train and test prefs
    movies = prefs.keys()
    random.shuffle(movies)

    movies_train, movies_test = movies[:int(0.9 * len(movies))], movies[int(0.1 * len(movies)):]
    train = {m: prefs[m] for m in movies_train}
    test = {m: prefs[m] for m in movies_test}

    for movie in test:
        sim_distances = []
        sim_pearsons = []

        for other_movie in train:
            # Calculate distance using euclidean distance
            sim_distances.append((r.sim_distance(prefs, movie, other_movie), other_movie))
            # Calculate similarity using pearson
            sim_pearsons.append((r.sim_pearson(prefs, movie, other_movie), other_movie))

        # distance sort ascending
        sim_distances.sort()
        # similarity sort descending
        sim_pearsons.sort(reverse=True)

        # select 1st top of the list
        sim_most_related_movie = sim_distances[0][1]
        pear_most_related_movie = sim_pearsons[0][1]

        # Compare
        print 'Using euclidean distance : Actual movie = {}, Predicted movie = {}'.format(movie, sim_most_related_movie)
        print 'Using pearson similarity : Actual movie = {}, Predicted movie = {}'.format(movie, pear_most_related_movie)
