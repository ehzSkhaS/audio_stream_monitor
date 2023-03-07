#!/usr/bin/env python3
import subprocess

#  ffmpeg -i https://icecast.teveo.cu/McW3fLhs -hide_banner -y -vn -sn -dn -filter_complex "[0:a]showvolume,scale=1920:-1,pad=1920:1080:(ow-iw)/2[v]" -map '[v]' -map '0:a' -c:a copy vu.mp4
# ffmpeg -v 56 -i https://icecast.teveo.cu/McW3fLhs -hide_banner -y -vn -sn -dn -filter_complex showvolume l.mp4
# ffmpeg -nostats -i https://icecast.teveo.cu/McW3fLhs -filter_complex ebur128 -f null -

class StreamMonitor:   
    __ffmpeg_cmd_filters = {
        'max_level' : '',
        'peak_level' : '',
        'volume_detect' : '',
        'ebur128' : '',
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
                universal_newlines=True,
                text=True
            ) as p:
                while True:
                    line = p.stderr.readline()
                    if not line:
                        break
                    yield line
                    
                    
    def ffmpeg_max_level(self):
        maxs = {
            'max_ch1' : '',
            'max_ch2' : '',
        }
        
        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('max_level')):            
            m1 = i.find('1.Max_level=')
            m2 = i.find('2.Max_level=')
            if m1 != -1:
                maxs['max_ch1'] = i[m1 + 12 : -1]
            if m2 != -1:
                maxs['max_ch2'] = i[m2 + 12 : -1]
                yield maxs


    def ffmpeg_peak_level(self):
        peaks = {
            'peak_ch1' : '',
            'peak_ch2' : '',
        }
        
        for i in self.__ffmpeg_output_capture(self.__ffmpeg_cmd_filters.get('peak_level')):            
            p1 = i.find('1.Peak_level=')
            p2 = i.find('2.Peak_level=')
            if p1 != -1:
                peaks['peak_ch1'] = i[p1 + 13 : -1]
            if p2 != -1:
                peaks['peak_ch2'] = i[p2 + 13 : -1]
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
                    'target' : k[t + 7 : m - 4],
                    'M' : k[m + 3 : s - 1],
                    'S' : k[s + 3 : i - 5],
                    'I': k[i + 3: l - 7],
                    'LRA': k[l + 6 : -1]
                }
                yield r_dict
                
                
    def peak_bars(self):
        ######################################################################################################
        # | -96 db     | -83 db                                                         | -18 db    | -6 db  #
        # OOOOOOOOOOOOO#################################################################++++++++++++------   #
        # | 13 char    | 65 char                                                        | 12 char   | 6 char #
        # |         13 |                                                             78 |        90 |   96   #
        ######################################################################################################
        peak_note_ch1, iter_ch1 = 0, 0
        peak_note_ch2, iter_ch2 = 0, 0
        bar_sample = 'OOOOOOOOOOOOO#################################################################++++++++++++------'
        for i in self.ffmpeg_peak_level():
            print('                  -96 dB       -83 dB                                                           -18 dB      -6 dB ')
            if i['peak_ch1'] != '-inf':
                str_ch1 = i['peak_ch1']
                f_ch1 = 96 + round(float(str_ch1))
                bs_ch1 = bar_sample[:f_ch1]
                
                if f_ch1 >= peak_note_ch1 or not iter_ch1:
                    peak_note_ch1 = f_ch1
                    iter_ch1 = 10
                    bs_ch1 = bs_ch1[:peak_note_ch1] + '|' + bs_ch1[peak_note_ch1 + 1:]
                elif iter_ch1:
                    iter_ch1 -= 1
                    bs_ch1 = bs_ch1[:f_ch1] + (peak_note_ch1 - f_ch1 - 1) * ' ' + '|' + bs_ch1[peak_note_ch1 + 1:]
                    
                print(str_ch1 + ((11 - len(str_ch1)) * ' ') + 'CH1 dB', bs_ch1)
            if i['peak_ch2'] != '-inf':
                str_ch2 = i['peak_ch2']
                f_ch2 = 96 + round(float(str_ch2))
                bs_ch2 = bar_sample[:f_ch2]
                
                if f_ch2 >= peak_note_ch2 or not iter_ch2:
                    peak_note_ch2 = f_ch2
                    iter_ch2 = 10
                    bs_ch2 = bs_ch2[:peak_note_ch2] + '|' + bs_ch2[peak_note_ch2 + 1:]
                elif iter_ch2:
                    iter_ch2 -= 1
                    bs_ch2 = bs_ch2[:f_ch2] + (peak_note_ch2 - f_ch2 - 1) * ' ' + '|' + bs_ch2[peak_note_ch2 + 1:]
                    
                print(str_ch2 + ((11 - len(str_ch2)) * ' ') + 'CH2 dB', bs_ch2)


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