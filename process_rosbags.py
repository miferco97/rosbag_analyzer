import argparse
from operator import pos
from utils.rosbag_reader import RosbagReader
from utils.timeseries import interpolate_data, get_time_series
from utils.plot_functions import *
import signal

def signal_handler(sig, frame):
    plt.close()
    exit(0)

def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key not in dict1:
            dict1[key] = value
        else:
            dict1[key].update(value)
    return dict1


def main(args: argparse.Namespace):
    # print the rosbag paths provided
    print(f'Processing {len(args.bagpath)} rosbags.')
    merged_data = {}
    for path in args.bagpath:
        print(f'Processing rosbag: {path}')

        bag = RosbagReader(path, args.start, args.end, update_header=True)
        topics = ['self_localization/pose']

        data_collection = {}
        interpolated_data = {}
        if args.namespaces is None:
            args.namespaces = ['']
            print('No namespaces provided, reading from the root namespace.')
        for namespace in args.namespaces:
            data = bag.read(topics, namespace=namespace)
            data_collection[namespace] = data
            merged_data = merge_dicts(merged_data, data_collection)


    data_collection = merged_data
    # print(f'data_collection: {data_collection}')
    time_series = get_time_series(data_collection, args.step)

    print(f'Collected data from {len(args.namespaces)} namespaces.')

    for namespace, data in data_collection.items():
        for topic, msgs in data.items():
            if topic not in interpolated_data:
                interpolated_data[topic] = {}
            interpolated_data[topic] = interpolate_data(msgs, time_series)
            print(f"Namespace: {namespace}, Topic: {topic} has {len(interpolated_data[topic])} interpolated messages.")

    # Plot the data
    plot_data=[]
    for topic, msgs in interpolated_data.items():
        if topic.find('self_localization/pose') != -1:
            plot_data.append(convert_into_plottable_data(msgs))

    if not len(plot_data):
        print('No data to plot.')
        return

    # plot3Dlines(plot_data,labels=list(interpolated_data.keys()),colors=['r','b'])
    print(f'Plotting {len(plot_data)} topics.')
    print(f'Plotting {len(plot_data[0])} axis.')
    print(f'Plotting {len(plot_data[0][0])} points.')

    plot3DlinesBIS(plot_data,labels=list(interpolated_data.keys()),colors=['r','b'])

    plt.show()



if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='Process rosbags and extract data from them, this data can be used for plotting or other purposes.')
    parser.add_argument('bagpath', type=str, nargs='+', help='Paths to the rosbags to process.')
    parser.add_argument('--namespaces', type=str, nargs='+', help='List of namespaces to read topics from.')
    parser.add_argument('--start', type=float, help='Start time to read messages from.', default=0.0)
    parser.add_argument('--end', type=float, help='End time to read messages from.', default=float('inf'))
    parser.add_argument('--step', type=float, help='Step time to process the messages.', default=0.1)
    
    main(parser.parse_args())
