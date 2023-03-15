#!/usr/bin/env python3
import subprocess


class FFmpegFilter:
    def __init__(self, url="https://icecast.teveo.cu/b3jbfThq"):
        self.__ffmpeg_cmd_filters = {
            'max_level': [
                'ffmpeg',
                '-re',
                '-i', url,
                '-hide_banner',
                '-y', '-vn', '-sn', '-dn',
                '-af',
                'astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.1.Max_level,ametadata=mode=print:key=lavfi.astats.2.Max_level',
                '-f', 'null',
                '-'
            ],
            'peak_level': [
                'ffmpeg',
                '-re',
                '-i', url,
                '-hide_banner',
                '-y', '-vn', '-sn', '-dn',
                '-af',
                'astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.1.Peak_level,ametadata=mode=print:key=lavfi.astats.2.Peak_level',
                '-f', 'null',
                '-'
            ],
            'volume_detect': [
                'ffmpeg',
                '-re',
                '-i', url,
                '-hide_banner',
                '-y', '-vn', '-sn', '-dn',
                '-af', 'volumedetect',
                '-f', 'null',
                '-t', '0.1',
                '-'
            ],
            'ebur128': [
                'ffmpeg',
                '-re',
                '-i', url,
                '-hide_banner',
                '-y', '-vn', '-sn', '-dn',
                '-filter_complex', 'ebur128',
                '-f', 'null',
                '-'
            ],
            'show_volume_v1': [
                'ffmpeg',
                '-re',
                '-i', url,
                '-hide_banner',
                '-y', '-vn', '-sn', '-dn',
                '-filter_complex', 'showvolume=f=0.5:c=VOLUME:b=4',
                '-f', 'null',
                '-t', '3',
                '-'
            ],
            'show_volume_v2': [
                'ffmpeg',
                '-re',
                '-i', url,
                '-hide_banner',
                '-y', '-vn', '-sn', '-dn',
                '-filter_complex', 'showvolume',
                '-f', 'null',
                '-t', '10',
                '-'
            ]
        }

    def __ffmpeg_output_capture(self, cmd, url=''):
        mod_cmd = cmd
        if url:
            mod_cmd[3] = url

        with subprocess.Popen(
            mod_cmd,
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
        maxs = {
            'max_ch1': '',
            'max_ch2': ''
        }

        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('max_level'), url):
            m1 = i.find('1.Max_level=')
            m2 = i.find('2.Max_level=')
            if m1 != -1:
                maxs['max_ch1'] = i[m1 + 12: -1]
            if m2 != -1:
                maxs['max_ch2'] = i[m2 + 12: -1]
                yield maxs

    def ffmpeg_peak_level(self, url=''):
        peaks = {
            'peak_ch1': '',
            'peak_ch2': ''
        }

        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('peak_level'), url):
            p1 = i.find('1.Peak_level=')
            p2 = i.find('2.Peak_level=')
            e1 = i.find('HTTP error 404')
            e2 = i.find('Error in the pull function')
            if p1 != -1:
                peaks['peak_ch1'] = i[p1 + 13: -1]
            if p2 != -1:
                peaks['peak_ch2'] = i[p2 + 13: -1]
                yield peaks
            if e1 != -1:
                yield 404
            if e2 != -1:
                yield 500

    def ffmpeg_volume_detect(self, url=''):
        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('volume_detect'), url):
            li = i.find('mean_volume: ')
            if li != -1:
                yield i[li + 13: -4]

    def ffmpeg_ebur128(self, url=''):
        for k in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('ebur128'), url):
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
