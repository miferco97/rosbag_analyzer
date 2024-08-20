import argparse
from operator import pos
from utils.rosbag_reader import RosbagReader
from utils.timeseries import interpolate_data, get_time_series
from utils.plot_functions import *


def main(args: argparse.Namespace):
    bag = RosbagReader(args.bagpath, args.start, args.end, update_header=True)
    topics = ['self_localization/pose']

    data_collection = {}
    interpolated_data = {}
    if args.namespaces is None:
        args.namespaces = ['']
        print('No namespaces provided, reading from the root namespace.')
    for namespace in args.namespaces:
        data = bag.read(topics, namespace=namespace)
        data_collection[namespace] = data
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

    plot3Dlines(plot_data,labels=list(interpolated_data.keys()))

    plt.show()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process rosbags and extract data from them, this data can be used for plotting or other purposes.')
    parser.add_argument('bagpath', type=str, help='Path to the rosbag file.')
    parser.add_argument('--namespaces', type=str, nargs='+', help='List of namespaces to read topics from.')
    parser.add_argument('--start', type=float, help='Start time to read messages from.', default=0.0)
    parser.add_argument('--end', type=float, help='End time to read messages from.', default=float('inf'))
    parser.add_argument('--step', type=float, help='Step time to process the messages.', default=0.1)
    
    main(parser.parse_args())
