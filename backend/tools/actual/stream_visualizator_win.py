#!/usr/bin/env python3
import argparse
import curses
import threading

import ffmpeg_filter


class StreamVisualizator:
    def __init__(self, screen):
        self.ffmpeg = ffmpeg_filter.FFmpegFilter()
        self.screen = screen
        self.win = None
        self.w_flag = False
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def peak_bars(self, y_pos, x_pos, url='', smooth=0):
        self.ffmpeg.change_filter_url('peak_level', url)

        self.win = curses.newwin(5, 92, y_pos, x_pos)

        ch_name = ('peak_ch1', 'peak_ch2')
        ch_peak_sample = {
            0: [0, 0],
            1: [0, 0]
        }
        bar_sample = '||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
        bar_empty_sample = '                                                                      '
        sample_counter = 0
        for i in self.ffmpeg.ffmpeg_peak_level():
            if sample_counter == smooth:
                sample_counter = 0

                self.win.addstr(0, 28, self.ffmpeg.get_filter_url('peak_level'))
                self.win.addstr(1, 18, '-70 dB')
                self.win.addstr(1, 70, '-18 dB')
                self.win.addstr(1, 82, '-6 dB')

                for k in range(2):
                    if i[ch_name[k]] != '-inf':
                        str_ch = i[ch_name[k]]
                        int_ch = round(float(str_ch))
                        if int_ch < -70:
                            int_ch = 0
                        else:
                            int_ch += 70
                        bs_ch = bar_sample[:int_ch]
                        ch_info = str_ch + ((11 - len(str_ch)) * ' ') + 'CH' + str(k + 1) + ' dB '

                        bar_yellow = ''
                        bar_green = ''
                        bar_red = ''
                        bar_blank = bar_empty_sample[:70 - int_ch]
                        if int_ch == 70:
                            bar_yellow = bs_ch[:52]
                            bar_green = bs_ch[52:64]
                            bar_red = bs_ch[64:70]
                        elif int_ch >= 64:
                            bar_yellow = bs_ch[:52]
                            bar_green = bs_ch[52:64]
                            bar_red = bs_ch[64:int_ch]
                        elif int_ch >= 52:
                            bar_yellow = bs_ch[:52]
                            bar_green = bs_ch[52:int_ch]
                        else:
                            bar_yellow = bs_ch[:int_ch]

                        len_ch_info = len(ch_info)
                        len_bar_yellow = len(bar_yellow)
                        len_bar_green = len(bar_green)
                        len_bar_red = len(bar_red)

                        self.w_flag = False

                        self.win.addstr(
                            k + 2,
                            len_ch_info + 73,
                            '|'
                        )
                        self.win.addstr(
                            k + 2,
                            0,
                            ch_info
                        )
                        self.win.addstr(
                            k + 2,
                            len_ch_info,
                            bar_yellow,
                            curses.color_pair(228) | curses.A_BOLD
                        )
                        self.win.addstr(
                            k + 2,
                            len_ch_info + len_bar_yellow,
                            bar_green,
                            curses.color_pair(48) | curses.A_BOLD
                        )
                        self.win.addstr(
                            k + 2,
                            len_ch_info + len_bar_yellow + len_bar_green,
                            bar_red,
                            curses.color_pair(198) | curses.A_BOLD
                        )
                        self.win.addstr(
                            k + 2,
                            len_ch_info + len_bar_yellow + len_bar_green + len_bar_red,
                            bar_blank
                        )

                        if int_ch > ch_peak_sample[k][0]:
                            ch_peak_sample[k][0] = int_ch
                            ch_peak_sample[k][1] = 40
                        elif ch_peak_sample[k][1] and ch_peak_sample[k][0]:
                            self.win.addstr(
                                k + 2,
                                len_ch_info + ch_peak_sample[k][0],
                                '|',
                                curses.color_pair(46) | curses.A_BOLD
                            )
                            ch_peak_sample[k][0] -= 1
                            ch_peak_sample[k][1] -= 1
                # self.screen.clear()
                # self.screen.refresh()
                # self.win.refresh()
                self.w_flag = True
            else:
                sample_counter += 1


def main(stdscr, args):
    vu1 = StreamVisualizator(stdscr)
    vu2 = StreamVisualizator(stdscr)
    vu3 = StreamVisualizator(stdscr)
    vu4 = StreamVisualizator(stdscr)
    vu5 = StreamVisualizator(stdscr)
    vu6 = StreamVisualizator(stdscr)
    vu7 = StreamVisualizator(stdscr)
    vu8 = StreamVisualizator(stdscr)
    vu9 = StreamVisualizator(stdscr)

    thread_pool = []

    vu_obj = [vu1, vu2, vu3, vu4, vu5, vu6, vu7, vu8, vu9]

    source = ''
    jump = 0
    if args['source']:
        source = args['source']
    if args['jump']:
        jump = args['jump']

    t1 = threading.Thread(target=vu1.peak_bars, args=[0, 0, "https://icecast.teveo.cu/7NgVjcqX", jump])
    t2 = threading.Thread(target=vu2.peak_bars, args=[5, 0, "https://icecast.teveo.cu/b3jbfThq", jump])
    t3 = threading.Thread(target=vu3.peak_bars, args=[10, 0, "https://icecast.teveo.cu/McW3fLhs", jump])
    t4 = threading.Thread(target=vu4.peak_bars, args=[15, 0, "https://icecast.teveo.cu/zrXXWK9F", jump])
    t5 = threading.Thread(target=vu5.peak_bars, args=[20, 0, "https://icecast.teveo.cu/XjfW7qWN", jump])
    t6 = threading.Thread(target=vu6.peak_bars, args=[25, 0, "https://icecast.teveo.cu/Nbtz7HT3", jump])
    t7 = threading.Thread(target=vu7.peak_bars, args=[30, 0, "https://icecast.teveo.cu/9Rnrbjzq", jump])
    t8 = threading.Thread(target=vu8.peak_bars, args=[35, 0, "https://icecast.teveo.cu/3MCwWg3V", jump])
    t9 = threading.Thread(target=vu9.peak_bars, args=[40, 0, "https://icecast.teveo.cu/Jdq3Rbrg", jump])

    thread_pool.append(t1)
    thread_pool.append(t2)
    thread_pool.append(t3)
    thread_pool.append(t4)
    thread_pool.append(t5)
    thread_pool.append(t6)
    thread_pool.append(t7)
    thread_pool.append(t8)
    thread_pool.append(t9)
    try:
        # pass
        # stdscr.refresh()
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t9.start()

        while True:
            for i in vu_obj:
                if i.w_flag:
                    i.win.refresh()
                    i.w_flag = False
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
