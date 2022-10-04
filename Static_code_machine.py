import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split


# pca计算
def pca_sklearn(data):
    pca = PCA()
    new_data = pca.fit_transform(data)
    return new_data


# ridge计算
def ridge_sklearn(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.2,shuffle=False)
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    y_predication = model.predict(X_test)
    res = np.array(y_train)
    res = np.append(res,y_predication)
    return res


if __name__ == "__main__":
    mat = [
        [2, 2.7, 5.6],
        [2.0, 1.6, 4.2],
        [1.0, 1.1, 0.7],
        [1.5, 1.6, 8.7],
        [1.1, 0.9, 5.3],
        [2.5, 2.4, 4.3],
        [0.5, 0.7, 2.6],
        [2.2, 2.9, 3.5],
        [1.9, 2.2, 0.5],
        [3.1, 3., 2.1],
    ]
    data = np.array(mat)
    newData = pca_sklearn(data)
    y = [1, 9, 8, 7, 4, 5, 6, 3, 2, 0]
    ridge_sklearn(newData, y)
    print(newData)
