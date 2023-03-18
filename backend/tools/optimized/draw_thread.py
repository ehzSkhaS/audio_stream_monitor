#!/usr/bin/env python3
import time
import threading


class DrawThread(threading.Thread):
    def __init__(self, stream_visualizator_obj, win_data_index) -> None:
        threading.Thread.__init__(self)
        self.__stop = threading.Event()
        self.__svo = stream_visualizator_obj
        self.__win_url_dict = stream_visualizator_obj.win_data[win_data_index]

    def get_win_pos(self) -> tuple:
        return self.__win_url_dict['win'].getbegyx()

    def get_win(self) -> dict:
        return self.__win_url_dict

    def stop(self) -> None:
        self.__stop.set()

    def stopped(self) -> None:
        return self.__stop.isSet()

    def run(self) -> None:
        for data in self.__svo.ffmpeg.ffmpeg_peak_level(self.__win_url_dict['url']):
            if self.stopped():
                data[0].terminate()
                break
            self.__svo.fill_win(self.__win_url_dict, data[1])
            if data[1] == 404 or data[1] == 500:
                time.sleep(10)
                self.run()
