#!/usr/bin/env python3
import os
import subprocess
from colorama import init, Fore, Style


class StreamMonitor:
    __ffmpeg_cmd_filters = {
        'max_level': '',
        'peak_level': '',
        'volume_detect': '',
        'ebur128': '',
        'show_volume_v1': '',
        'show_volume_v2': ''
    }

    def __init__(self, url):
        self.__ffmpeg_cmd_filters['max_level'] = [
            'ffmpeg',
            '-re',
            '-i', url,
            '-hide_banner',
            '-y', '-vn', '-sn', '-dn',
            '-af',
            'astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.1.Max_level,ametadata=mode=print:key=lavfi.astats.2.Max_level',
            '-f', 'null',
            '-'
        ]
        self.__ffmpeg_cmd_filters['peak_level'] = [
            'ffmpeg',
            '-re',
            '-i', url,
            '-hide_banner',
            '-y', '-vn', '-sn', '-dn',
            '-af',
            'astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.1.Peak_level,ametadata=mode=print:key=lavfi.astats.2.Peak_level',
            '-f', 'null',
            '-'
        ]
        self.__ffmpeg_cmd_filters['volume_detect'] = [
            'ffmpeg',
            '-re',
            '-i', url,
            '-hide_banner',
            '-y', '-vn', '-sn', '-dn',
            '-af', 'volumedetect',
            '-f', 'null',
            '-t', '0.1',
            '-'
        ]
        self.__ffmpeg_cmd_filters['ebur128'] = [
            'ffmpeg',
            '-re',
            '-i', url,
            '-hide_banner',
            '-y', '-vn', '-sn', '-dn',
            '-filter_complex', 'ebur128',
            '-f', 'null',
            '-'
        ]
        self.__ffmpeg_cmd_filters['show_volume_v1'] = [
            'ffmpeg',
            '-i', url,
            '-hide_banner',
            '-y', '-vn', '-sn', '-dn',
            '-filter_complex', 'showvolume=f=0.5:c=VOLUME:b=4',
            '-f', 'null',
            '-t', '3',
            '-'
        ]
        self.__ffmpeg_cmd_filters['show_volume_v2'] = [
            'ffmpeg',
            '-v', '56',
            '-re',
            '-i', url,
            '-hide_banner',
            '-y', '-vn', '-sn', '-dn',
            '-filter_complex', 'showvolume',
            '-f', 'null',
            '-t', '10',
            '-'
        ]

    def __ffmpeg_output_capture(self, cmd):
        with subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        ) as p:
            while True:
                line = p.stderr.readline()
                if not line:
                    break
                yield line

    def ffmpeg_max_level(self):
        maxs = {
            'max_ch1': '',
            'max_ch2': '',
        }

        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('max_level')):
            m1 = i.find('1.Max_level=')
            m2 = i.find('2.Max_level=')
            if m1 != -1:
                maxs['max_ch1'] = i[m1 + 12: -1]
            if m2 != -1:
                maxs['max_ch2'] = i[m2 + 12: -1]
                yield maxs

    def ffmpeg_peak_level(self):
        peaks = {
            'peak_ch1': '',
            'peak_ch2': '',
        }

        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('peak_level')):
            p1 = i.find('1.Peak_level=')
            p2 = i.find('2.Peak_level=')
            if p1 != -1:
                peaks['peak_ch1'] = i[p1 + 13: -1]
            if p2 != -1:
                peaks['peak_ch2'] = i[p2 + 13: -1]
                yield peaks

    def ffmpeg_volume_detect(self):
        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('volume_detect')):
            li = i.find('mean_volume: ')
            if li != -1:
                yield i[li + 13: -4]

    def ffmpeg_ebur128(self):
        for k in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('ebur128')):
            t = k.find('TARGET:')
            m = k.find('M: ')
            s = k.find('S: ')
            i = k.find('I: ')
            l = k.find('LRA: ')
            if t != -1 and m != -1 and s != -1 and i != -1 and l != -1:
                r_dict = {
                    'target': k[t + 7: m - 4],
                    'M': k[m + 3: s - 1],
                    'S': k[s + 3: i - 5],
                    'I': k[i + 3: l - 7],
                    'LRA': k[l + 6: -1]
                }
                yield r_dict

    def peak_bars(self):
        ######################################################################################################
        # | -96 db                                                                      | -18 db    | -6 db  #
        # OOOOOOOOOOOOO#################################################################++++++++++++------   #
        # |                              78 char                                        | 12 char   | 6 char #
        ######################################################################################################
        if os.name != 'posix':
            init(convert=True)

        peak_note_ch1, iter_ch1 = 0, 0
        peak_note_ch2, iter_ch2 = 0, 0
        bar_sample = '##############################################################################++++++++++++------'
        for i in self.ffmpeg_peak_level():
            print(' ')
            print(' ')
            print('                  -96 dB                                                                        -18 dB      -6 dB ')
            if i['peak_ch1'] != '-inf':
                str_ch1 = i['peak_ch1']
                f_ch1 = 96 + round(float(str_ch1))
                bs_ch1 = bar_sample[:f_ch1]

                if f_ch1 >= peak_note_ch1 or not iter_ch1:
                    peak_note_ch1 = f_ch1
                    iter_ch1 = 10
                    bs_ch1 = bs_ch1[:peak_note_ch1] + \
                        '|' + bs_ch1[peak_note_ch1 + 1:]
                elif iter_ch1:
                    iter_ch1 -= 1
                    bs_ch1 = bs_ch1[:f_ch1] + (peak_note_ch1 - f_ch1 - 1) * \
                        ' ' + '|' + bs_ch1[peak_note_ch1 + 1:]

                bar_yellow = ''
                bar_green = ''
                bar_red = ''
                size = len(bs_ch1)
                if size == 96:
                    bar_yellow = bs_ch1[:78]
                    bar_green = bs_ch1[78:90]
                    bar_red = bs_ch1[90:96]
                elif size >= 90:
                    bar_yellow = bs_ch1[:78]
                    bar_green = bs_ch1[78:90]
                    bar_red = bs_ch1[90:size]
                elif size >= 78:
                    bar_yellow = bs_ch1[:78]
                    bar_green = bs_ch1[78:size]
                else:
                    bar_yellow = bs_ch1[:size]
                print(str_ch1 + ((11 - len(str_ch1)) * ' ') + 'CH1 dB', Fore.YELLOW +
                      bar_yellow, Fore.GREEN + bar_green, Fore.RED + bar_red)
                print(Style.RESET_ALL)
            if i['peak_ch2'] != '-inf':
                str_ch2 = i['peak_ch2']
                f_ch2 = 96 + round(float(str_ch2))
                bs_ch2 = bar_sample[:f_ch2]

                if f_ch2 >= peak_note_ch2 or not iter_ch2:
                    peak_note_ch2 = f_ch2
                    iter_ch2 = 10
                    bs_ch2 = bs_ch2[:peak_note_ch2] + \
                        '|' + bs_ch2[peak_note_ch2 + 1:]
                elif iter_ch2:
                    iter_ch2 -= 1
                    bs_ch2 = bs_ch2[:f_ch2] + (peak_note_ch2 - f_ch2 - 1) * \
                        ' ' + '|' + bs_ch2[peak_note_ch2 + 1:]

                bar_yellow = ''
                bar_green = ''
                bar_red = ''
                size = len(bs_ch2)
                if size == 96:
                    bar_yellow = bs_ch2[:78]
                    bar_green = bs_ch2[78:90]
                    bar_red = bs_ch2[90:96]
                elif size >= 90:
                    bar_yellow = bs_ch2[:78]
                    bar_green = bs_ch2[78:90]
                    bar_red = bs_ch2[90:size]
                elif size >= 78:
                    bar_yellow = bs_ch2[:78]
                    bar_green = bs_ch2[78:size]
                else:
                    bar_yellow = bs_ch2[:size]
                print(str_ch2 + ((11 - len(str_ch2)) * ' ') + 'CH2 dB', Fore.YELLOW +
                      bar_yellow, Fore.GREEN + bar_green, Fore.RED + bar_red)
                print(Style.RESET_ALL)
            print(' ')
            print(' ')


def main():
    monitor = StreamMonitor("https://icecast.teveo.cu/7NgVjcqX")  # vitral
    # monitor = StreamMonitor("https://icecast.teveo.cu/b3jbfThq")  # radio reloj

    monitor.peak_bars()

    # for i in monitor.ffmpeg_max_level():
    #     print(i)

    # for i in monitor.ffmpeg_peak_level():
    #     print(i)

    # for i in monitor.ffmpeg_volume_detect():
    #     print(int(float(i)*-1) * '-')

    # for i in monitor.ffmpeg_ebur128():
    #     print(i)


if __name__ == "__main__":
    main()
