#!/usr/bin/env python3
import curses
import argparse
import subprocess


class StreamMonitor:
    __ffmpeg_cmd_filters = {
        'max_level': '',
        'peak_level': '',
        'volume_detect': '',
        'ebur128': '',
        'show_volume_v1': '',
        'show_volume_v2': ''
    }

    def __init__(self, url="https://icecast.teveo.cu/b3jbfThq"):
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

    def ffmpeg_max_level(self, url=''):
        if url:
            self.__ffmpeg_cmd_filters.get('max_level')[3] = url

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

    def ffmpeg_peak_level(self, url=''):
        if url:
            self.__ffmpeg_cmd_filters.get('peak_level')[3] = url

        peaks = {
            'peak_ch1': '',
            'peak_ch2': '',
            'url': url
        }

        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('peak_level')):
            p1 = i.find('1.Peak_level=')
            p2 = i.find('2.Peak_level=')
            if p1 != -1:
                peaks['peak_ch1'] = i[p1 + 13: -1]
            if p2 != -1:
                peaks['peak_ch2'] = i[p2 + 13: -1]
                yield peaks

    def ffmpeg_volume_detect(self, url=''):
        if url:
            self.__ffmpeg_cmd_filters.get('volume_detect')[3] = url

        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('volume_detect')):
            li = i.find('mean_volume: ')
            if li != -1:
                yield i[li + 13: -4]

    def ffmpeg_ebur128(self, url=''):
        if url:
            self.__ffmpeg_cmd_filters.get('ebur128')[3] = url

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

    def peak_bars(self, screen, y_pos, x_pos, url='', smooth=0):
        if url:
            self.__ffmpeg_cmd_filters.get('peak_level')[3] = url

        screen.addstr(
            y_pos,
            x_pos + 28,
            self.__ffmpeg_cmd_filters.get('peak_level')[3]  # url
        )
        screen.addstr(
            y_pos + 1,
            x_pos + 18,
            '-70 dB'
        )
        screen.addstr(
            y_pos + 1,
            x_pos + 70,
            '-18 dB'
        )
        screen.addstr(
            y_pos + 1,
            x_pos + 82,
            '-6 dB'
        )
        ch_name = ('peak_ch1', 'peak_ch2')
        ch_peak_sample = {
            0: [0, 0],
            1: [0, 0]
        }
        bar_sample = '||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
        bar_empty_sample = '                                                                      '
        sample_counter = 0
        for i in self.ffmpeg_peak_level():
            if sample_counter == smooth:
                sample_counter = 0
                for k in range(2):
                    if i[ch_name[k]] != '-inf':
                        str_ch = i[ch_name[k]]
                        int_ch = 70 + round(float(str_ch))
                        bs_ch = bar_sample[:int_ch]
                        ch_info = str_ch + ((11 - len(str_ch)) * ' ') + 'CH' + str(k + 1) + ' dB '

                        bar_yellow = ''
                        bar_green = ''
                        bar_red = ''
                        bar_blank = bar_empty_sample[:70 - int_ch]
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

                        len_ch_info = len(ch_info)
                        len_bar_yellow = len(bar_yellow)
                        len_bar_green = len(bar_green)
                        len_bar_red = len(bar_red)
                        screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + 71,
                            '|'
                        )
                        screen.addstr(
                            y_pos + k + 2,
                            x_pos,
                            ch_info
                        )
                        screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info,
                            bar_yellow,
                            curses.color_pair(228) | curses.A_BOLD
                        )
                        screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + len_bar_yellow,
                            bar_green,
                            curses.color_pair(48) | curses.A_BOLD
                        )
                        screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + len_bar_yellow + len_bar_green,
                            bar_red,
                            curses.color_pair(198) | curses.A_BOLD
                        )
                        screen.addstr(
                            y_pos + k + 2,
                            x_pos + len_ch_info + len_bar_yellow + len_bar_green + len_bar_red,
                            bar_blank
                        )

                        if int_ch > ch_peak_sample[k][0]:
                            ch_peak_sample[k][0] = int_ch
                            ch_peak_sample[k][1] = 40
                        elif ch_peak_sample[k][1] and ch_peak_sample[k][0]:
                            screen.addstr(
                                y_pos + k + 2,
                                x_pos + len_ch_info + ch_peak_sample[k][0],
                                '|',
                                curses.color_pair(46) | curses.A_BOLD
                            )
                            ch_peak_sample[k][0] -= 1
                            ch_peak_sample[k][1] -= 1

                screen.refresh()
            else:
                sample_counter += 1


def main(stdscr, args):
    source = ''
    jump = 0
    if args['source']:
        source = args['source']
    if args['jump']:
        jump = args['jump']

    monitor = StreamMonitor()

    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    for i in range(curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    try:
        monitor.peak_bars(stdscr, 0, 0, source, jump)
    except KeyboardInterrupt:
        curses.endwin()

    # monitor = StreamMonitor("https://icecast.teveo.cu/7NgVjcqX")  # vitral
    # monitor = StreamMonitor("https://icecast.teveo.cu/b3jbfThq")  # radio reloj

    # for i in monitor.ffmpeg_peak_level():
    #     print(i)

    # for i in monitor.ffmpeg_max_level():
    #     print(i)

    # for i in monitor.ffmpeg_volume_detect():
    #     print(i)

    # for i in monitor.ffmpeg_ebur128("https://icecast.teveo.cu/b3jbfThq"):
    #     print(i)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = '''\
        Basic Interface for Stream VU
        -----------------------------
          for my cool boss: ALAMINO
                enyoy it!
        '''

    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.add_argument(
        "-s",
        "--source",
        metavar='AUDIO_STREAM',
        type=str,
        help='url or path to an audio stream or file'
    )
    parser.add_argument(
        "-j",
        "--jump",
        metavar='INTEGER',
        type=int,
        help='number of samples to jump without capture'
    )
    args = vars(parser.parse_args())

    if args.values():
        curses.wrapper(main, args)
    else:
        curses.wrapper(main, '')
