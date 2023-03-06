#!/usr/bin/env python3
import os
import queue
import sys
import subprocess
import multiprocessing

# ffmpeg -re -i https://icecast.teveo.cu/McW3fLhs -hide_banner -y -vn -sn -dn -af astats=metadata=1:reset=0.3,ametadata=print:key=lavfi.astats.Overall.Peak_level -f null -t 3 /dev/null
# ffmpeg -re -i https://icecast.teveo.cu/McW3fLhs -hide_banner -y -vn -sn -dn -af astats=metadata=1:reset=0.3,ametadata=mode=print:key=lavfi.astats.Overall.Peak_level:file='pipe\:2' -f null -t 3 /dev/null
# ffmpeg -v 40 -re -i https://icecast.teveo.cu/McW3fLhs -hide_banner -y -vn -sn -dn -af astats=metadata=1:reset=0.3,ametadata=mode=print:key=lavfi.astats.Overall.Peak_level -f null -t 3 -


class StreamMonitor:
    url = ''
    info_dict = {
        'radio_station' : '',
        'codec' : '',
        'sample_rate' : '',
        'channels' : '',
        'bit_rate' : ''
    }
    
    def __init__(self, url):
        self.url = url
    
    def stream_info(self):
        import ffmpeg
        
        try:
            print('Opening Stream...')
            info = ffmpeg.probe(self.url)
            streams = info.get('streams', [])
            self.info_dict['radio_station'] = info.get('format', '').get('tags','').get('icy-name', '')
            self.info_dict['codec'] = streams[0].get('codec_name')
            self.info_dict['sample_rate'] = int(streams[0].get('sample_rate'))
            self.info_dict['channels'] = int(streams[0].get('channels'))
            self.info_dict['bit_rate'] = int(streams[0].get('bit_rate'))
            print(self.info_dict)
            print('******************************************************')
            print(info)
        except ffmpeg.Error as e:
            sys.stderr.buffer.write(e.stderr)
            
            
    def _peak_level_filter(self):
        process = subprocess.Popen([
            'ffmpeg',
            '-re',
            '-i', 
            self.url,
            '-hide_banner',
            '-y',
            '-vn',
            '-sn',
            '-dn', 
            '-af',
            'astats=metadata=1:reset=0.3,ametadata=print:key=lavfi.astats.Overall.Peak_level',
            '-f',
            'null',
            '-t',
            '3',
            'pipe:'
        ],stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        
        
    def test_whatever3(self):
        ffmpeg_complex_filter = "astats=metadata=1:reset=0.3,ametadata=mode=print:key=lavfi.astats.Overall.Peak_level"
        with subprocess.Popen([
            'ffmpeg',
            '-v',
            '40',
            '-re',
            '-i', 
            self.url,
            '-hide_banner',
            '-y',
            '-vn',
            '-sn',
            '-dn', 
            '-af',
            ffmpeg_complex_filter,    
            '-f',
            'null',
            '-t',
            '3',
            '-'
        ], stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True) as process:            
            while True:
                line = process.stderr.readline()
                print(line)
                if not line:                    
                    break

                
    def _ffmpeg_output_capture(self, cmd):
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
                
                
    def test_fcapture(self):
        cmd = [
            'ffmpeg',
            '-v',
            '40',
            '-re',
            '-i', 
            self.url,
            '-hide_banner',
            '-y',
            '-vn',
            '-sn',
            '-dn', 
            '-af',
            'astats=metadata=1:reset=0.3,ametadata=mode=print:key=lavfi.astats.Overall.Peak_level',
            '-f',
            'null',
            '-t',
            '3',
            '-'
        ]
        
        for i in self._ffmpeg_output_capture(cmd):
            print(i)
        

def main():
    monitor = StreamMonitor("https://icecast.teveo.cu/McW3fLhs")
    # monitor.stream_info()
    monitor.test_fcapture()


if __name__ == "__main__":
    main()