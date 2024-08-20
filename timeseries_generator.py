import numpy as np
from utils.interpolation_functions import interpolate


class TimeSeries():
    """ Class that collects the data from a topic and interpolates it to a time series.
    Note that the interpolation between the data points is linear and must be implemented in the Interpolate method."""


