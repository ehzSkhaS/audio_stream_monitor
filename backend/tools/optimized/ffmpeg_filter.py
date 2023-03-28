#!/usr/bin/env python3
import subprocess


class FFmpeg_HTTP_404(Exception):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "ERROR 404: Stream Not Found"


class FFmpeg_HTTP_500(Exception):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "ERROR 500: Internal Server Error"


class FFmpeg_HTTP_502(Exception):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return "ERROR 502: Bad Gateway"


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


def __error_detect(line):
    e1 = line.find('HTTP error 404')
    e2 = line.find('Error in the pull function')
    e3 = line.find('HTTP error 502 Bad Gateway')
    if e1 != -1:
        raise FFmpeg_HTTP_404()
    elif e2 != -1:
        raise FFmpeg_HTTP_500()
    elif e3 != -1:
        raise FFmpeg_HTTP_502()


def ffmpeg_peak_level(sub_p, url) -> tuple:
    peaks = {
        'peak_ch1': '',
        'peak_ch2': ''
    }

    for i in __ffmpeg_output_capture(__ffmpeg_cmd_filters.get('peak_level'), sub_p, url):
        __error_detect(i)
        p1 = i.find('1.Peak_level=')
        p2 = i.find('2.Peak_level=')
        if p1 != -1:
            peaks['peak_ch1'] = i[p1 + 13: -1]
        if p2 != -1:
            peaks['peak_ch2'] = i[p2 + 13: -1]
            yield peaks


def ffmpeg_max_level(sub_p, url) -> tuple:
    maxs = {
        'max_ch1': '',
        'max_ch2': ''
    }

    for i in __ffmpeg_output_capture(__ffmpeg_cmd_filters.get('max_level'), sub_p, url):
        __error_detect(i)
        m1 = i.find('1.Max_level=')
        m2 = i.find('2.Max_level=')
        if m1 != -1:
            maxs['max_ch1'] = i[m1 + 12: -1]
        if m2 != -1:
            maxs['max_ch2'] = i[m2 + 12: -1]
            yield maxs


def ffmpeg_volume_detect(sub_p, url):
    for i in __ffmpeg_output_capture(__ffmpeg_cmd_filters.get('volume_detect'), sub_p, url):
        __error_detect(i)
        li = i.find('mean_volume: ')
        if li != -1:
            yield i[li + 13: -4]


def ffmpeg_ebur128(sub_p, url) -> dict:
    for k in __ffmpeg_output_capture(__ffmpeg_cmd_filters.get('ebur128'), sub_p, url):
        __error_detect(k)
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
