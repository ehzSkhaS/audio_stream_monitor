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
            win_pos = self.__sv.calc_pos(win_index)
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

    def deploy_refresh_thread(self) -> None:
        twr = threading.Thread(target=self.__sv.win_refresh)
        twr.start()

    def launch_input_capture(self) -> None:
        self.__sv.capture_input(self.__thread_pool)

    def launch(self) -> None:
        self.deploy_draw_threads()
        self.deploy_refresh_thread()
        self.launch_input_capture()
