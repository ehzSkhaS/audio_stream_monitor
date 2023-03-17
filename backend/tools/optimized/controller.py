#!/usr/bin/env python3
import os
import csv
import sys
import time
import curses
import argparse
import threading

import draw_thread
import stream_visualizator


def main(stdscr, args):
    sv = stream_visualizator.StreamVisualizator(stdscr)
    thread_pool = []

    source = []
    jump = 0
    if args['source']:
        source = args['source']
    else:
        try:
            with open(f'{os.path.dirname(__file__)}/data.csv', newline='') as source_data:
                for row in csv.DictReader(source_data):
                    source.append('https://icecast.teveo.cu/' + row['url'])
        except IOError as error:
            stdscr.addstr(0, 0, str(error))
            stdscr.refresh()
            curses.napms(3000)
            sys.exit(0)
    if args['jump']:
        jump = args['jump']

    try:
        win_index = 0
        for i in source:
            win_pos = sv.calc_pos(win_index)
            if win_pos:
                stdscr.addstr(win_pos[0], win_pos[1], f'Loading... {i}')
                stdscr.refresh()
                sv.create_win(win_pos[0], win_pos[1], i)
                dt = draw_thread.DrawThread(sv, len(sv.win_data) - 1)
                thread_pool.append(dt)
                thread_pool[-1].start()
                win_index += 1
                time.sleep(1)
            else:
                break

        twr = threading.Thread(
            target=sv.win_refresh
        )
        twr.start()

        tis = threading.Thread(
            target=sv.input_stream,
            args=thread_pool
        )
        tis.start()
    except KeyboardInterrupt:
        # curses.reset_shell_mode()
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
        # curses.def_shell_mode()
    else:
        curses.wrapper(main, '')
        # curses.def_shell_mode()
