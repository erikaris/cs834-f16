from numpy import genfromtxt, array, random
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.neighbors import KNeighborsClassifier

if __name__ == '__main__':
    # Read data ratings.csv from movielens
    ratings = genfromtxt('ratings.csv', delimiter=',', skip_header=1, usecols=range(3))

    # Split data to train and test data, with ratio train:test = 0.9:0.1
    random.shuffle(ratings)
    train, test = ratings[len(ratings)/10:, :], ratings[:len(ratings)/10, :]

    # Train data using KNN, get 1st top neighbor
    neigh = KNeighborsClassifier(n_neighbors=1)
    # X = 2-dimensional array, y = target = 1st col of X
    neigh.fit(train, train[:, 0])
    # Get neighbors indices (2-dimensional array)
    distances, neighbors_indices = neigh.kneighbors(test)
    # Get ratings from indices
    euclidean_neighbors = array([train[ns[0]] for ns in neighbors_indices])

    # Train data using Pearson
    lr = LinearRegression()
    # X = 2-dimensional array, y = target = 1st col of X
    lr.fit(train, train[:, 0])
    # Get neighbors index (1-dimensional array)
    neighbors_idx = lr.predict(test)
    # Get ratings from indices
    pearson_neighbors = array([train[int(idx)] for idx in neighbors_idx])

    # Get MSE of predicted ratings, for both euclidean and pearson
    y_true = []
    for user, movie, rating in test:
        y_true.append(rating)

    y_pred_euc = []
    for user, movie, rating in euclidean_neighbors:
        y_pred_euc.append(rating)

    y_pred_pear = []
    for user, movie, rating in pearson_neighbors:
        y_pred_pear.append(rating)

    print "Mean Squared Error of Euclidean: %f" % mean_squared_error(y_true, y_pred_euc)
    print "Mean Squared Error of Pearson: %f" % mean_squared_error(y_true, y_pred_pear)
