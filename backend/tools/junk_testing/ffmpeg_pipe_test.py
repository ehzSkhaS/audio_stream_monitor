#!/usr/bin/env python3
import sys
import ffmpeg
import subprocess

# ffmpeg -re -i https://icecast.teveo.cu/3MCwWg3V -hide_banner -y -vn -sn -dn -af astats=metadata=1:reset=0.3,ametadata=print:key=lavfi.astats.Overall.Peak_level -f null -t 10 /dev/null

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
            
            
    def volume_levels(self):
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
            'pipe:2'
        ], stdout=subprocess.PIPE, universal_newlines=True, bufsize=1)
        
        # while True:
        #     process.stdout.
    


def main():
    monitor = StreamMonitor("https://icecast.teveo.cu/McW3fLhs")
    # monitor.stream_info()
    monitor.volume_levels()

if __name__ == "__main__":
    main()