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
        }

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
            'max_ch2': ''
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
            'peak_ch2': ''
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

    def change_filter_url(self, filtername, url):
        if self.__ffmpeg_cmd_filters.get(filtername) and url:
            self.__ffmpeg_cmd_filters.get(filtername)[3] = url
            return True
        return False

    def get_filter_url(self, filtername):
        if self.__ffmpeg_cmd_filters.get(filtername):
            return self.__ffmpeg_cmd_filters.get(filtername)[3]
        return None
