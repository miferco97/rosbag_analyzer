import numpy as np
from utils.interpolation_functions import interpolate, update_header
from utils.ros2_utils import stamp_to_float

def get_time_series(data_collection:dict[str,dict[str,any]], step_size:float = 0.1):
    """ Returns the time series of the data."""
    initial_time = 0
    end_time = 0
    for _, data in data_collection.items():
        for _, list_data in data.items():
            for msg in list_data:
                if hasattr(msg, 'header'):
                    t = stamp_to_float(msg.header.stamp)
                    initial_time = min(initial_time, t)
                    end_time = max(end_time, t)
    return np.arange(initial_time, end_time, step=step_size)


def interpolate_data(data:list, time_series:np.array):
    """ Interpolates the data to the time series.
    We consider that the data is ordered by time."""
    index_1 = 0
    index_2 = 1
    interpolated_data = []
    i = 0
    while i < len(time_series):
        msg_1 = data[index_1]
        msg_2 = data[index_2]
        t1 = stamp_to_float(msg_1.header.stamp)
        t2 = stamp_to_float(msg_2.header.stamp)
        t = time_series[i]
        if t < t1:
            interpolated_data.append(msg_1)
            interpolated_data[-1] = update_header(interpolated_data[-1], time_series[i])
            i += 1
        elif t1 <= t <= t2:
            interpolated_data.append(interpolate(msg_1, msg_2, t))
            interpolated_data[-1] = update_header(interpolated_data[-1], time_series[i])
            i += 1
        else:
            # if t is greater than t2 we need to update the indexes
            if index_2 == len(data) - 1:
                interpolated_data.append(msg_2)
                i += 1
                continue
            index_1 += 1
            index_2 += 1

    # print(f'Interpolated data from {len(data)} messages to {len(interpolated_data)} messages.')
    return interpolated_data



                    

