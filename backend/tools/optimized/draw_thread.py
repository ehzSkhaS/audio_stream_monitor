#!/usr/bin/env python3
import threading

import ffmpeg_filter


class DrawThread(threading.Thread):
    def __init__(self, stream_visualizator_obj, win_data_index) -> None:
        threading.Thread.__init__(self)
        self.__stop = threading.Event()
        self.__pause = threading.Event()
        self.__svo = stream_visualizator_obj
        self.__win_data_dict = stream_visualizator_obj.win_data[win_data_index]

    def get_win_pos(self) -> tuple:
        return self.__win_data_dict['win'].getbegyx()

    def get_win_data_dict(self) -> dict:
        return self.__win_data_dict

    def stop(self) -> None:
        self.__stop.set()

    def stopped(self) -> bool:
        return self.__stop.isSet()

    def pause(self) -> None:
        self.__pause.clear()

    def paused(self) -> bool:
        return not self.__pause.isSet()

    def play(self) -> None:
        self.__pause.set()

    def run(self) -> None:
        self.__exec_block()

    def __exec_block(self) -> None:
        sub_p = []
        for data in ffmpeg_filter.ffmpeg_peak_level(sub_p, self.__win_data_dict['url']):
            if self.stopped():
                sub_p[0].terminate()
                break
            self.__svo.fill_win(self.__win_data_dict, data)
            if data == 404 or data == 500:
                self.pause()
                sub_p[0].terminate()
                break
        if self.paused():
            self.__pause.wait(10.0)
            self.__exec_block()
