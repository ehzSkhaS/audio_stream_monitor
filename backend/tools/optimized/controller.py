#!/usr/bin/env python3
import os
import csv
import sys
import time
import curses
import threading

import draw_thread
import stream_visualizator


class Controller:
    UP = 1
    DOWN = 0

    def __init__(self, screen) -> None:
        self.__screen = screen
        self.__sv = stream_visualizator.StreamVisualizator(screen)
        self.__jump = 0
        self.__thread_pool = []

    def load_data(self) -> None:
        try:
            with open(f'{os.path.dirname(__file__)}/data.csv', newline='') as source_data:
                rows = [x for x in csv.DictReader(source_data)]
                rows = reversed(rows)
                for row in rows:
                    self.__sv.lower_url_stack.put(f'https://icecast.teveo.cu/{row["url"]}')
        except IOError as error:
            self.__screen.addstr(0, 0, str(error))
            self.__screen.refresh()
            curses.napms(3000)
            sys.exit(0)

    def set_data(self, source) -> None:
        for i in reversed(source):
            self.__sv.lower_url_stack.append(i)

    def set_jump(self, jump) -> None:
        self.__jump = jump

    def deploy_draw_threads(self) -> None:
        win_index = 0
        while self.__sv.lower_url_stack.qsize():
            win_pos = self.__sv.position_win(win_index)
            if win_pos:
                url = self.__sv.lower_url_stack.get()
                self.__screen.addstr(win_pos[0], win_pos[1], f'Loading... {url}')
                self.__screen.refresh()
                self.__sv.create_win(win_pos[0], win_pos[1], url)
                dt = draw_thread.DrawThread(self.__sv, len(self.__sv.win_data) - 1)
                self.__thread_pool.append(dt)
                self.__thread_pool[-1].start()
                win_index += 1
                time.sleep(0.2)
            else:
                break

    def capture_input(self) -> None:
        while True:
            ch = self.__screen.getch()
            if ch == 0x1b or ch == 0x51 or ch == 0x71:
                for i in self.__thread_pool:
                    wd = i.get_win_data_dict()
                    self.__sv.close_win(wd['win'])
                    self.__sv.win_data.remove(wd)
                    i.stop()
                    if i.paused():
                        i.play()
                    i.join()
                self.__screen.keypad(False)
                curses.echo()
                curses.endwin()
                break
            elif ch == curses.KEY_UP:
                self.__scroll(self.UP)
            elif ch == curses.KEY_DOWN:
                self.__scroll(self.DOWN)

    def __scroll(self, scroll_dir) -> None:
        if scroll_dir and self.__sv.lower_url_stack.qsize():
            top_threads = []
            win_max_y_pos, win_max_x_pos = self.__sv.getmaxyx_win()
            del win_max_x_pos
            for t in self.__thread_pool:
                win_data_dict = t.get_win_data_dict()
                win_y_pos, win_x_pos = win_data_dict['win'].getbegyx()

                if not win_y_pos:
                    self.__sv.upper_url_stack.put(win_data_dict['url'])
                    win_data_dict['url'] = self.__sv.lower_url_stack.get()
                    top_threads.append(t)
                    t.pause()
                    win_data_dict['win'].erase()
                    win_data_dict['win'].mvwin(win_max_y_pos, win_x_pos)
                else:
                    win_data_dict['win'].erase()
                    win_data_dict['win'].mvwin(win_y_pos - 5, win_x_pos)

            for t in top_threads:
                t.play()

        if not scroll_dir and self.__sv.upper_url_stack.qsize():
            bottom_threads = []
            win_max_y_pos, win_max_x_pos = self.__sv.getmaxyx_win()
            del win_max_x_pos
            for t in self.__thread_pool:
                win_data_dict = t.get_win_data_dict()
                win_y_pos, win_x_pos = win_data_dict['win'].getbegyx()

                if win_y_pos == win_max_y_pos:
                    self.__sv.lower_url_stack.put(win_data_dict['url'])
                    win_data_dict['url'] = self.__sv.upper_url_stack.get()
                    bottom_threads.append(t)
                    t.pause()
                    win_data_dict['win'].erase()
                    win_data_dict['win'].mvwin(0, win_x_pos)
                else:
                    win_data_dict['win'].erase()
                    win_data_dict['win'].mvwin(win_y_pos + 5, win_x_pos)

            for t in bottom_threads:
                t.play()

    def deploy_refresh_thread(self) -> None:
        twr = threading.Thread(target=self.__sv.refresh_win)
        twr.start()

    def launch(self) -> None:
        self.deploy_draw_threads()
        self.deploy_refresh_thread()
        self.capture_input()
