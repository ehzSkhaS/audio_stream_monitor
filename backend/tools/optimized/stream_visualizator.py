#!/usr/bin/env python3
import queue
import curses


class StreamVisualizator:
    BAR_SAMPLE = '||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
    BAR_EMPTY_SAMPLE = '                                                                      '
    BAR_ROWS = 5
    BAR_COLS = 98
    PEAK_CH_NAME = ('peak_ch1', 'peak_ch2')
    UP = 1
    DOWN = 0

    def __init__(self, screen) -> None:
        screen.keypad(True)
        self.win_data = []
        self.screen = screen
        self.screen_height, self.screen_width = screen.getmaxyx()
        self.bar_height_amount = self.screen_height // self.BAR_ROWS
        self.bar_width_amount = self.screen_width // self.BAR_COLS
        self.upper_url_stack = queue.LifoQueue()
        self.lower_url_stack = queue.LifoQueue()
        curses.curs_set(0)
        curses.noecho()
        curses.start_color()
        curses.use_default_colors()

        for i in range(curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def create_win(self, y_pos, x_pos, url) -> dict:
        win_data_dict = {
            'win': curses.newwin(self.BAR_ROWS, self.BAR_COLS, y_pos, x_pos),
            'url': url,
            'peaks': {
                0: [0, 0],
                1: [0, 0]
            }
        }
        self.win_data.append(win_data_dict)
        return win_data_dict

    def print_error(self, win, msg):
        win.erase()
        win.addstr(2, round(48 - len(msg) / 2), msg)
        win.addstr(3, 33, 'Reconnecting every 10 sec...')

    def fill_win(self, win_data_dict, data) -> None:
        win = win_data_dict['win']
        url = win_data_dict['url']
        ch_peak_sample = win_data_dict['peaks']

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

        win.addstr(0, 28, url)
        win.addstr(1, 18, '-70 dB')
        win.addstr(1, 70, '-18 dB')
        win.addstr(1, 82, '-6 dB')

    def win_refresh(self) -> None:
        while len(self.win_data):
            for i in self.win_data:
                if i['win'].is_wintouched():
                    i['win'].refresh()

    def calc_pos(self, win_index) -> tuple:
        if self.screen_height >= self.BAR_ROWS and self.screen_width >= self.BAR_COLS:
            if win_index < self.bar_height_amount * self.bar_width_amount:
                y_pos = (win_index // self.bar_width_amount) * self.BAR_ROWS
                x_pos = (win_index % self.bar_width_amount) * self.BAR_COLS
                return (y_pos, x_pos)
            else:
                return None
        else:
            return None

    def capture_input(self, thread_pool) -> None:
        while True:
            ch = self.screen.getch()
            if ch == 0x1b or ch == 0x51 or ch == 0x71:
                for i in thread_pool:
                    wd = i.get_win_data_dict()
                    wd['win'].untouchwin()
                    wd['win'].addstr(1, 44, 'CLOSING...')
                    wd['win'].refresh()
                    self.win_data.remove(wd)
                    if i.paused():
                        i.play()
                    i.stop()
                    i.join()
                self.screen.keypad(False)
                curses.echo()
                curses.endwin()
                break
            elif ch == curses.KEY_UP:
                self.scroll(thread_pool, self.UP)
            elif ch == curses.KEY_DOWN:
                self.scroll(thread_pool, self.DOWN)

    def scroll(self, thread_pool, scroll_dir) -> None:
        pass
        # if scroll_dir and self.lower_url_stack.qsize():
        #     index = 0
        #     for t in thread_pool:
        #         t_y, t_x = t.get_win_pos()
        #         if t_y == index * self.bar_height_amount:
        #             if not index:
