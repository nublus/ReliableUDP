import argparse


def readArg():
    parser = argparse.ArgumentParser(description='Receive files using GBN or SR protocol.')
    parser.add_argument('protocol', choices=['GBN', 'SR'], default='GBN', help='Specify the protocol to use (GBN or SR)')
    parser.add_argument('-N', '--window-size', type=int, default=4, help='Window size (number of packets)')
    parser.add_argument('-T', '--timeout', type=float, default=2.0, help='Timeout in seconds')
    parser.add_argument('filename', help='Name of the file to receive')
    args = parser.parse_args()

    protocol = args.protocol
    window_size = args.window_size
    timeout = args.timeout
    filename = args.filename
    
    return  protocol, window_size, timeout, filename
