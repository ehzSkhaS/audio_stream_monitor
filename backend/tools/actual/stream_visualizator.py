#!/usr/bin/env python3
import curses
import argparse
import ffmpeg_filter


class StreamVisualizator:
    def __init__(self, screen=None):
        self.ffmpeg = ffmpeg_filter.FFmpegFilter()
        if screen:
            self.screen = screen
        else:
            self.screen = curses.initscr()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def peak_bars(self, y_pos, x_pos, url='', smooth=0):
        self.ffmpeg.change_filter_url('peak_level', url)

        self.screen.addstr(
            y_pos,
            x_pos + 28,
            self.ffmpeg.get_filter_url('peak_level')
        )
        self.screen.addstr(
            y_pos + 1,
            x_pos + 18,
            '-70 dB'
        )
        self.screen.addstr(
            y_pos + 1,
            x_pos + 70,
            '-18 dB'
        )
        self.screen.addstr(
            y_pos + 1,
            x_pos + 82,
            '-6 dB'
        )
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
                for k in range(2):
                    if i[ch_name[k]] != '-inf':
                        str_ch = i[ch_name[k]]
                        int_ch = 70 + round(float(str_ch))
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
                        self.screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + 71,
                            '|'
                        )
                        self.screen.addstr(
                            y_pos + k + 2,
                            x_pos,
                            ch_info
                        )
                        self.screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info,
                            bar_yellow,
                            curses.color_pair(228) | curses.A_BOLD
                        )
                        self.screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + len_bar_yellow,
                            bar_green,
                            curses.color_pair(48) | curses.A_BOLD
                        )
                        self.screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + len_bar_yellow + len_bar_green,
                            bar_red,
                            curses.color_pair(198) | curses.A_BOLD
                        )
                        self.screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + len_bar_yellow + len_bar_green + len_bar_red,
                            bar_blank
                        )

                        if int_ch > ch_peak_sample[k][0]:
                            ch_peak_sample[k][0] = int_ch
                            ch_peak_sample[k][1] = 40
                        elif ch_peak_sample[k][1] and ch_peak_sample[k][0]:
                            self.screen.addstr(
                                y_pos + k + 2,
                                x_pos + len_ch_info + ch_peak_sample[k][0],
                                '|',
                                curses.color_pair(46) | curses.A_BOLD
                            )
                            ch_peak_sample[k][0] -= 1
                            ch_peak_sample[k][1] -= 1

                self.screen.refresh()
            else:
                sample_counter += 1

    def screen_calc():
        pass


def main(stdscr, args):
    vu = StreamVisualizator(stdscr)

    ################### Peak Bars #####################
    source = ''
    jump = 0
    if args['source']:
        source = args['source']
    if args['jump']:
        jump = args['jump']

    try:
        vu.peak_bars(0, 0, source, jump)
    except KeyboardInterrupt:
        curses.endwin()
    ###################################################

    # monitor = StreamMonitor("https://icecast.teveo.cu/7NgVjcqX")  # vitral
    # monitor = StreamMonitor("https://icecast.teveo.cu/b3jbfThq")  # radio reloj

    # for i in monitor.ffmpeg_peak_level():
    #     print(i)

    # for i in monitor.ffmpeg_max_level():
    #     print(i)

    # for i in monitor.ffmpeg_volume_detect():
    #     print(i)

    # for i in monitor.ffmpeg_ebur128("https://icecast.teveo.cu/b3jbfThq"):
    #     print(i)


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
