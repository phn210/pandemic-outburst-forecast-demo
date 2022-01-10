import pandas as pd
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import curve_fit


def array_to_single_index(arr):
    return arr[0]


def sir_solver(t,beta,gamma,prev,x0):

    def sir(x,t,beta,gamma,prev):
        s = x[0]
        i = x[1]
        r = x[2]
        dsdt = -prev*beta*s*i
        didt = prev*beta*s*i - gamma*i
        drdt = gamma*i
        return [dsdt,didt,drdt]

    y = odeint(sir,x0,t,args=(beta,gamma,prev,)) 
    return y


def ModelSolution(t,beta,gamma,prev,x0):
    s = sir_solver(t,beta,gamma,prev,x0)
    return s[:,2]


def optimize(points, START, END, rate_ir):

    def fit_normal(data,t_start,t_end):
        t = np.linspace(t_start,t_end,t_end-t_start+1)
        x0 = [1-(rate_ir+1)*data[0],rate_ir*data[0],data[0]]
        bounds = (0,[np.inf,1])
        f = lambda t,beta,gamma: ModelSolution(t,beta,gamma,1,x0) 
        p = curve_fit(f,t,data,bounds=bounds)
        return p
  
    p1=fit_normal(points,START,END)
    p = [p1[0][0],p1[0][1],1]
    return p


def simulate(p, points, START, END, rate_ir):
    t = np.linspace(START,END,END-START+1)       
    x0 = [1-(rate_ir+1)*points[0],rate_ir*points[0],points[0]]
    y = sir_solver(t,p[0],p[1],1,x0)
    return y


def predict(df, x):
    days_since_lst = []
    length = len(df)
    for i in range(length):
        days_since_lst.append(i)

    date = np.array(df['ObservationDate'])
    X_raw = np.array(df["Confirmed"])  # .reshape(-1,1)
    absolute = lambda x: int(x)/(98562173) # 98562173 ~ Country/province's population  
    X_train = np.array([ absolute(xi) for xi in X_raw ])
    # X is the world cases array
    y_train = np.array(days_since_lst).reshape(-1, 1)

    for i in range(length, length + x):
        days_since_lst.append(i)
    y = np.array(days_since_lst).reshape(-1, 1)

    days_since_lst = []
    for i in range(length, length + x):
        days_since_lst.append(i)

    y_test = np.array(days_since_lst).reshape(-1, 1)
    
    RATE_IR = 0.15

    params = optimize(X_train, length - 61, length-1, RATE_IR)

    y_pred = simulate(params, X_train, length - 61, length-1, RATE_IR)

    for i in range(x):
        X_train = numpy.append(X_train, 0)
        date = numpy.append(date, 'Null')
    
    return {
        "sir_pred_y" : list(map(array_to_single_index, y.tolist())),
        "sir_pred_x": y_pred.tolist(),
        "train_data_y": list(map(array_to_single_index, y_train.tolist())),
        "train_data_x" : X_train.tolist(),
        "dates": date.tolist()
    }
