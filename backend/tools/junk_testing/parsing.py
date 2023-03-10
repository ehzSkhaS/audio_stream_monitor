#!/usr/bin/env python3
import argparse


def main(args):
    print('hello')
    print('this are the args:', args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = '''\
        Basic Interface for Stream VU
        -----------------------------
                enyoy it!
        '''

    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.add_argument("-s", "--source", metavar='AUDIO_STREAM', type=str, help='url or path to an audio stream or file')
    args = vars(parser.parse_args())

    if args['source']:
        print('yeap')
        main(args)
    else:
        main('')
