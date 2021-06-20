import numpy as np
from math import dist, fabs, sqrt


def CalculateRMSE(data1,data2):
    value = 0
    n = len(data1)
    for i in range(n):
        value += pow(data1[i]-data2[i],2)
    return sqrt(value/n)

def Calculate3Derror(data1,data2,speed=False):
    metric= ' m'
    if speed:
        metric = ' m/s'

    dists = np.sqrt(np.sum(np.power(data1- data2,2),axis=0))
    MSE = np.sum(dists,axis=0)/len(dists)
    print("\t GLOBAL RMSE =" , MSE,metric)
    return MSE, dists
    

def axesbyaxesRMSE(positions1,positions2,speed=False):
    metric= ' m'
    if speed:
        metric = ' m/s'

    print("\t RMSE in x-axis =" , CalculateRMSE(positions1[0,:],positions2[0,:]),metric)
    print("\t RMSE in y-axis =" , CalculateRMSE(positions1[1,:],positions2[1,:]),metric)
    print("\t RMSE in z-axis =" , CalculateRMSE(positions1[2,:],positions2[2,:]),metric)



