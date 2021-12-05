import numpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
import ntpath
import os
from sklearn.pipeline import make_pipeline

def array_to_single_index(arr):
    return arr[0]

def predict(df, x):
    days_since_lst = []
    length = len(df)
    for i in range(length):
        days_since_lst.append(i)

    date = np.array(df['ObservationDate'])
    X_train = np.array(df["Confirmed"])  # .reshape(-1,1)
    # X is the world cases array
    y_train = np.array(days_since_lst).reshape(-1, 1)

    for i in range(length, length + x):
        days_since_lst.append(i)
    y = np.array(days_since_lst).reshape(-1, 1)

    days_since_lst = []
    for i in range(length, length + x):
        days_since_lst.append(i)

    y_test = np.array(days_since_lst).reshape(-1, 1)

    poly = PolynomialFeatures(degree=6)
    poly_y_train = poly.fit_transform(y_train)
    poly_y_test = poly.fit_transform(y_test)
    poly_y = poly.fit_transform(y)

    linear_model = make_pipeline(StandardScaler(with_mean=False), LinearRegression())
    linear_model.fit(poly_y_train, X_train)
    test_linear_pred = linear_model.predict(poly_y_test)
    linear_pred = linear_model.predict(poly_y)

    for i in range(x):
        X_train = numpy.append(X_train, 0)
        date = numpy.append(date, 'Null')
    
    return {
        "linear_pred_y" : list(map(array_to_single_index, y.tolist())),
        "linear_pred_x": linear_pred.tolist(),
        "train_data_y": list(map(array_to_single_index, y_train.tolist())),
        "train_data_x" : X_train.tolist()
    }
