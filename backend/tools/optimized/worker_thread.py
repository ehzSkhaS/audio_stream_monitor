#!/usr/bin/env python3
import csv
import sys
import time
import curses
import argparse
import threading

import stream_visualizator


class WorkerThread(threading.Thread):
    def __init__(self, vu_obj, y_pos, x_pos, url, jump):
        threading.Thread.__init__(self)
        self.__vu = vu_obj
        self.__y_pos = y_pos
        self.__x_pos = x_pos
        self.__url = url
        self.__jump = jump

    def run(self):
        self.__vu.peak_bars(self.__y_pos, self.__x_pos, self.__url, self.__jump)


def main(stdscr, args):
    vu = stream_visualizator.StreamVisualizator(stdscr)
    thread_pool = []

    source = []
    jump = 0
    if args['source']:
        source = args['source']
    else:
        try:
            with open('data.csv', newline='') as source_data:
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
            win_pos = vu.calc_pos(win_index)
            if win_pos:
                stdscr.addstr(win_pos[0], win_pos[1], f'Loading... {i}')
                stdscr.refresh()
                thread_pool.append(
                    threading.Thread(
                        target=vu.peak_bars,
                        args=[win_pos[0], win_pos[1], i, jump],
                    )
                )
                thread_pool[-1].start()
                win_index += 1
                time.sleep(1)
            else:
                break

        twr = threading.Thread(target=vu.win_refresh)
        twr.start()

        tis = threading.Thread(target=vu.input_stream)
        tis.start()
    except KeyboardInterrupt:
        for i in vu.win_list:
            del i
        # curses.reset_shell_mode()
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
