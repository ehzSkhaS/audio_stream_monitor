#!/usr/bin/env python3
import subprocess


__ffmpeg_cmd_filters = {
    'peak_level': [
        'ffmpeg',
        '-re',
        '-i', ' ',
        '-hide_banner',
        '-y', '-vn', '-sn', '-dn',
        '-af',
        'astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.1.Peak_level,ametadata=mode=print:key=lavfi.astats.2.Peak_level',
        '-f', 'null',
        '-'
    ],
    'max_level': [
        'ffmpeg',
        '-re',
        '-i', ' ',
        '-hide_banner',
        '-y', '-vn', '-sn', '-dn',
        '-af',
        'astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.1.Max_level,ametadata=mode=print:key=lavfi.astats.2.Max_level',
        '-f', 'null',
        '-'
    ],
    'volume_detect': [
        'ffmpeg',
        '-re',
        '-i', ' ',
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
        '-i', ' ',
        '-hide_banner',
        '-y', '-vn', '-sn', '-dn',
        '-filter_complex', 'ebur128',
        '-f', 'null',
        '-'
    ]
}


def __ffmpeg_output_capture(cmd, sub_p, url) -> tuple:
    mod_cmd = cmd
    mod_cmd[3] = url

    with subprocess.Popen(
        mod_cmd,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    ) as p:
        sub_p.append(p)
        while True:
            line = p.stderr.readline()
            if not line:
                break
            yield line


def ffmpeg_peak_level(sub_p, url) -> tuple:
    peaks = {
        'peak_ch1': '',
        'peak_ch2': ''
    }

    for i in __ffmpeg_output_capture(__ffmpeg_cmd_filters.get('peak_level'), sub_p, url):
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

# def ffmpeg_max_level(self, url) -> tuple:
#     maxs = {
#         'max_ch1': '',
#         'max_ch2': ''
#     }

#     for i in self.__ffmpeg_output_capture(ffmpeg_cmd_filters.get('max_level'), url):
#         m1 = i[1].find('1.Max_level=')
#         m2 = i[1].find('2.Max_level=')
#         if m1 != -1:
#             maxs['max_ch1'] = i[m1 + 12: -1]
#         if m2 != -1:
#             maxs['max_ch2'] = i[m2 + 12: -1]
#             yield (i[0], maxs)

# def ffmpeg_volume_detect(self, url='') -> tuple:
#     for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('volume_detect'), url):
#         li = i[1].find('mean_volume: ')
#         if li != -1:
#             yield (i[0], i[1][li + 13: -4])

# def ffmpeg_ebur128(self, url='') -> tuple:
#     for k in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('ebur128'), url):
#         t = k[1].find('TARGET:')
#         m = k[1].find('M: ')
#         s = k[1].find('S: ')
#         i = k[1].find('I: ')
#         l = k[1].find('LRA: ')
#         if t != -1 and m != -1 and s != -1 and i != -1 and l != -1:
#             r_dict = {
#                 'target': k[1][t + 7: m - 4],
#                 'M': k[1][m + 3: s - 1],
#                 'S': k[1][s + 3: i - 5],
#                 'I': k[1][i + 3: l - 7],
#                 'LRA': k[1][l + 6: -1]
#             }
#             yield (k[0], r_dict)
