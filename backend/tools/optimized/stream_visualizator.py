#!/usr/bin/env python3
import time
import curses

import ffmpeg_filter


class StreamVisualizator:
    BAR_SAMPLE = '||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
    BAR_EMPTY_SAMPLE = '                                                                      '
    PEAK_CH_NAME = ('peak_ch1', 'peak_ch2')

    def __init__(self):
        self.ffmpeg = ffmpeg_filter.FFmpegFilter()
        self.win_list = []
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def peak_bars(self, y_pos, x_pos, url, smooth=0):
        win = curses.newwin(5, 96, y_pos, x_pos)
        self.win_list.append(win)
        ch_peak_sample = {
            0: [0, 0],
            1: [0, 0]
        }
        sample_counter = 0
        recall = False

        for i in self.ffmpeg.ffmpeg_peak_level(url):
            if sample_counter == smooth:
                sample_counter = 0

                win.addstr(0, 28, url)
                win.addstr(1, 18, '-70 dB')
                win.addstr(1, 70, '-18 dB')
                win.addstr(1, 82, '-6 dB')

                if i == 404:
                    win.addstr(2, 40, 'ERROR: 404 Not Found')
                    win.addstr(3, 38, 'Reconnecting every 10 sec...')
                    time.sleep(10)
                    recall = True
                    break
                else:
                    for k in range(2):
                        if i[self.PEAK_CH_NAME[k]] != '-inf':
                            str_ch = i[self.PEAK_CH_NAME[k]]
                            int_ch = round(float(str_ch))

                            if int_ch > 0:
                                int_ch = 0

                            if int_ch <= -70:
                                int_ch = 0
                            else:
                                int_ch += 70

                            ch_info = str_ch + ((11 - len(str_ch)) * ' ') + 'CH' + str(k + 1) + ' dB '
                            len_ch_info = len(ch_info)
                            bar_yellow = ''
                            bar_green = ''
                            bar_red = ''
                            bs_ch = self.BAR_SAMPLE[:int_ch]
                            bar_blank = self.BAR_EMPTY_SAMPLE[int_ch:]

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

                            win.addstr(k + 2, len_ch_info + 70, '|')
                            win.addstr(k + 2, 0, ch_info)
                            win.addstr(k + 2, len_ch_info, bar_yellow, curses.color_pair(228) | curses.A_BOLD)
                            win.addstr(bar_green, curses.color_pair(48) | curses.A_BOLD)
                            win.addstr(bar_red, curses.color_pair(198) | curses.A_BOLD)
                            win.addstr(bar_blank)

                            if int_ch > ch_peak_sample[k][0]:
                                ch_peak_sample[k][0] = int_ch
                                ch_peak_sample[k][1] = 40
                            elif ch_peak_sample[k][1]:
                                win.addstr(k + 2, len_ch_info + ch_peak_sample[k][0], '|', curses.color_pair(46) | curses.A_BOLD)
                                win.addstr(k + 2, 90, '-{:02} dB'.format((ch_peak_sample[k][0] - 70) * - 1), curses.color_pair(46) | curses.A_BOLD)
                                ch_peak_sample[k][1] -= 1
                            else:
                                ch_peak_sample[k][0] = 0
                                win.addstr(k + 2, 90, '-{:02} dB'.format((70)), curses.color_pair(46) | curses.A_BOLD)
                        else:
                            win.addstr(k + 2, 0, 'SILENCE')
            else:
                sample_counter += 1
        if recall:
            self.peak_bars(y_pos, x_pos, url)

    def scroll(self):
        pass
