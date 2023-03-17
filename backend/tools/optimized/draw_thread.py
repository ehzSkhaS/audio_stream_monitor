#!/usr/bin/env python3
import time
import threading


class DrawThread(threading.Thread):
    def __init__(self, stream_visualizator_obj, win_data_index):
        threading.Thread.__init__(self)
        self.__stop = threading.Event()
        self.__svo = stream_visualizator_obj
        self.__win_url_dict = stream_visualizator_obj.win_data[win_data_index]

    def stop(self):
        self.__stop.set()

    def stopped(self):
        return self.__stop.isSet()

    def run(self):
        for data in self.__svo.ffmpeg.ffmpeg_peak_level(self.__win_url_dict['url']):
            if self.stopped():
                return
            self.__svo.fill_win(self.__win_url_dict, data)
            if data == 404 or data == 500:
                time.sleep(10)
                self.run()

    def get_win_pos(self):
        return (self.__win_url_dict['win'].getbegyx())
