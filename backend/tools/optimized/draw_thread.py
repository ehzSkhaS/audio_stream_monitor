#!/usr/bin/env python3
import time
import threading
import warnings

import ffmpeg_filter


class TimeoutReport(threading.Thread):
    def __init__(self) -> None:
        threading.Thread.__init__(self)
        self.daemon = True
        self.__stop = threading.Event()

    def stop(self) -> None:
        self.__stop.set()

    def stopped(self) -> bool:
        return self.__stop.is_set()

    def restart(self):
        self.__stop.clear()
        self.__timeout_report()

    def setup(self, func, timeout, args):
        self.__func = func
        self.__timeout = timeout
        self.__args = args

    def run(self):
        self.__timeout_report()

    def __timeout_report(self):
        while not self.stopped() and self.__timeout:
            start_time = time.time()
            self.__func(self.__timeout, self.__args)
            end_time = time.time()

            if (end_time - start_time) < 1:
                time.sleep(1 - (end_time - start_time))

            self.__timeout -= 1


class DrawThread(threading.Thread):
    def __init__(self, stream_visualizator_obj, win_data_index) -> None:
        threading.Thread.__init__(self)
        self.daemon = True
        self.__restart = True
        self.__stop = threading.Event()
        self.__unpause = threading.Event()
        self.__report = TimeoutReport()
        self.__svo = stream_visualizator_obj
        self.__win_data_dict = stream_visualizator_obj.win_data[win_data_index]

    def get_win_data_dict(self) -> dict:
        return self.__win_data_dict

    def stop(self) -> None:
        self.__unpause.set()
        self.__stop.set()
        self.__restart = False

    def stopped(self) -> bool:
        return self.__stop.is_set()

    def pause(self) -> None:
        self.__unpause.clear()
        self.__restart = True

    def paused(self) -> bool:
        return not self.__unpause.is_set()

    def play(self) -> None:
        self.__unpause.set()

    def run(self) -> None:
        self.__unpause.set()
        self.__draw_thread()

    def __draw_thread(self) -> None:
        sub_p = []
        try:
            with warnings.catch_warnings(record=True) as w:
                data = ffmpeg_filter.ffmpeg_peak_level(sub_p, self.__win_data_dict['url'])
                while not self.__stop.is_set():
                    if len(w) > 0:
                        for warning in w:
                            self.__svo.warning_win(self.__win_data_dict, str(warning.message))

                    self.__svo.fill_win(self.__win_data_dict, next(data))

                # for data in ffmpeg_filter.ffmpeg_peak_level(sub_p, self.__win_data_dict['url']):
                #     if self.__stop.is_set():  # or not self.__unpause.is_set():
                #         break

                #     self.__svo.fill_win(self.__win_data_dict, data)

        except (ffmpeg_filter.FFmpeg_HTTP_404,
                ffmpeg_filter.FFmpeg_HTTP_408,
                ffmpeg_filter.FFmpeg_HTTP_500,
                ffmpeg_filter.FFmpeg_HTTP_502,
                ffmpeg_filter.FFmpeg_HTTP_522
                ) as e:
            self.__svo.error_win(self.__win_data_dict, str(e))
            self.__report.setup(self.__svo.timeout_report, 10, self.__win_data_dict)
            self.__report.restart()
            self.__unpause.clear()

        if self.__stop.is_set():
            sub_p[0].kill()
            # sub_p[1].stop()

            if self.__report.is_alive():
                self.__report.stop()
                self.__report.join(0.1)
        elif not self.__unpause.is_set():
            sub_p[0].kill()
            # sub_p[1].stop()
            self.__unpause.wait(10.0)

            if self.__report.is_alive():
                self.__report.stop()
                self.__report.join(0.1)

            if self.__restart:
                self.__draw_thread()
