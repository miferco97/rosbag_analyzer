import argparse
from rosbag_reader import RosbagReader


def main(args: argparse.Namespace):
    bag = RosbagReader(args.bagpath)
    topics = ['self_localization/pose']

    data_collection = {}
    for namespace in args.namespaces:
        data = bag.read(topics, namespace=namespace)
        data_collection[namespace] = data

    print(f'Collected data from {len(args.namespaces)} namespaces.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process rosbags and extract data from them, this data can be used for plotting or other purposes.')
    parser.add_argument('bagpath', type=str, help='Path to the rosbag file.')
    parser.add_argument('--namespaces', type=str, nargs='+', help='List of namespaces to read topics from.')
    parser.add_argument('--start_time', type=float, help='Start time to read messages from.', default=0.0)
    parser.add_argument('--end_time', type=float, help='End time to read messages from.', default=-1.0)
    parser.add_argument('--step', type=float, help='Step time to process the messages.', default=0.1)
    main(parser.parse_args())
