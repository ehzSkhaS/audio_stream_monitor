#!/usr/bin/env python3
import time
import curses
import argparse
import threading

import stream_visualizator


class WorkerThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.peak_bars_threads = []
        # self.screen_scroll_thread


def main(stdscr, args):
    vu = stream_visualizator.StreamVisualizator()
    thread_pool = []
    url_l = [
        "https://icecast.teveo.cu/7NgVjcqX",
        "https://icecast.teveo.cu/b3jbfThq",
        "https://icecast.teveo.cu/McW3fLhs",
        "https://icecast.teveo.cu/zrXXWK9F",
        "https://icecast.teveo.cu/XjfW7qWN",
        "https://icecast.teveo.cu/Nbtz7HT3",
        "https://icecast.teveo.cu/9Rnrbjzq",
        "https://icecast.teveo.cu/3MCwWg3V",
        "https://icecast.teveo.cu/Jdq3Rbrg",
        "https://icecast.teveo.cu/g73XCjCH"
        # "https://icecast.teveo.cu/ngcdcV3k",
    ]

    source = ''
    jump = 0
    if args['source']:
        source = args['source']
    if args['jump']:
        jump = args['jump']

    y_pos = 0
    for i in url_l:
        thread_pool.append(
            threading.Thread(
                target=vu.peak_bars,
                args=[y_pos, 0, i, jump]
            )
        )
        y_pos += 5

    try:
        for i in thread_pool:
            i.start()
            time.sleep(1)

        while True:
            for i in vu.win_list:
                if i.is_wintouched():
                    i.refresh()
    except KeyboardInterrupt:
        for i in thread_pool:
            i.join()
        curses.endwin()


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
