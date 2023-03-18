#!/usr/bin/env python3
import sys
import curses
import argparse

import controller


def main(stdscr, args):
    control = controller.Controller(stdscr)

    if args['source']:
        control.set_data(args['source'])
    else:
        control.load_data()

    if args['jump']:
        control.set_jump(args['jump'])

    try:
        control.launch()
        sys.exit(0)
    except KeyboardInterrupt:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = '''\
        Basic Interface for Stream VU
        -----------------------------
          for my cool boss: ALAMINO
                enyoy it!
        '''

    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.add_argument(
        "-s",
        "--source",
        nargs='+',
        default=[],
        metavar='AUDIO_STREAM',
        type=str,
        help='url or path to an audio stream or file'
    )
    parser.add_argument(
        "-j",
        "--jump",
        metavar='INTEGER',
        type=int,
        help='number of samples to jump without capture'
    )
    args = vars(parser.parse_args())

    if args.values():
        curses.wrapper(main, args)
    else:
        curses.wrapper(main, '')
