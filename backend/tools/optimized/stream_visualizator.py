#!/usr/bin/env python3
import time
import curses

import ffmpeg_filter


class StreamVisualizator:
    BAR_SAMPLE = '||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
    BAR_EMPTY_SAMPLE = '                                                                      '
    BAR_ROWS = 5
    BAR_COLS = 98
    PEAK_CH_NAME = ('peak_ch1', 'peak_ch2')
    UP = -1
    DOWN = 1

    def __init__(self, screen):
        self.ffmpeg = ffmpeg_filter.FFmpegFilter()
        self.win_data = []
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()

        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        self.screen = screen
        self.screen_height, self.screen_width = screen.getmaxyx()
        self.bar_height_amount = self.screen_height // self.BAR_ROWS
        self.bar_width_amount = self.screen_width // self.BAR_COLS

    def create_win(self, y_pos, x_pos, url):
        win_url_dict = {
            'win': curses.newwin(self.BAR_ROWS, self.BAR_COLS, y_pos, x_pos),
            'url': url,
            'peaks': {
                0: [0, 0],
                1: [0, 0]
            }
        }
        self.win_data.append(win_url_dict)
        return win_url_dict

    def fill_win(self, win_url_dict, data):
        win = win_url_dict['win']
        url = win_url_dict['url']
        ch_peak_sample = win_url_dict['peaks']

        # for i in self.ffmpeg.ffmpeg_peak_level(data['url']):
        win.addstr(0, 28, url)
        win.addstr(1, 18, '-70 dB')
        win.addstr(1, 70, '-18 dB')
        win.addstr(1, 82, '-6 dB')

        if data == 404:
            msg = 'ERROR: 404 Not Found'
            win.addstr(2, round(48 - len(msg) / 2), msg)
            win.addstr(3, 33, 'Reconnecting every 10 sec...')
        elif data == 500:
            msg = 'ERROR: 500 Internal Server Error'
            win.addstr(2, round(48 - len(msg) / 2), msg)
            win.addstr(3, 33, 'Reconnecting every 10 sec...')
        else:
            for k in range(2):
                if data[self.PEAK_CH_NAME[k]] != '-inf':
                    str_ch = data[self.PEAK_CH_NAME[k]]
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
                        win.addstr(k + 2, 90, '-{:02} dB  '.format((ch_peak_sample[k][0] - 70) * - 1), curses.color_pair(46) | curses.A_BOLD)
                        ch_peak_sample[k][1] -= 1
                    else:
                        ch_peak_sample[k][0] = 0
                        win.addstr(k + 2, 90, '-{:02} dB  '.format((70)), curses.color_pair(46) | curses.A_BOLD)
                else:
                    win.addstr(k + 2, 0, 'SILENCE')

    def win_refresh(self):
        if len(self.win_data):
            while True:
                for i in self.win_data:
                    if i['win'].is_wintouched():
                        i['win'].refresh()

    def calc_pos(self, win_index):
        if self.screen_height >= self.BAR_ROWS and self.screen_width >= self.BAR_COLS:
            if win_index < self.bar_height_amount:
                return (win_index * self.BAR_ROWS, 0)
            else:
                tmp_row = win_index // self.bar_height_amount
                if tmp_row < self.bar_width_amount:
                    return ((win_index % self.bar_height_amount) * self.BAR_ROWS, tmp_row * self.BAR_COLS)
                else:
                    return None
        else:
            return None

    def input_stream(self, thread_pool):
        while True:
            ch = self.screen.getch()
            if ch == curses.KEY_UP:
                self.scroll(self.UP)
            elif ch == curses.KEY_DOWN:
                self.scroll(self.DOWN)
            elif ch == curses.KEY_BACKSPACE:
                for i in thread_pool:
                    i.stop()
                    time.sleep(3)
                    if i.stopped():
                        i.join()

                curses.echo()
                curses.nocbreak()
                curses.endwin()

    def scroll(self, scroll_dir):
        for i in self.win_list:
            i.scroll(scroll_dir)
