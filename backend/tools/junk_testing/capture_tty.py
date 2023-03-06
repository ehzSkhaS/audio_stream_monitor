import errno
import os
import pty
import select
import subprocess

def tty_capture(cmd, bytes_input):
    """Capture the output of cmd with bytes_input to stdin,
    with stdin, stdout and stderr as TTYs.

    Based on Andy Hayden's gist:
    https://gist.github.com/hayd/4f46a68fc697ba8888a7b517a414583e
    """
    mo, so = pty.openpty()  # provide tty to enable line-buffering
    me, se = pty.openpty()  
    mi, si = pty.openpty()  

    p = subprocess.Popen(
        cmd,
        bufsize=1, stdin=si, stdout=so, stderr=se, 
        close_fds=True)
    for fd in [so, se, si]:
        os.close(fd)
    os.write(mi, bytes_input)

    timeout = 0.04  # seconds
    readable = [mo, me]
    result = {mo: b'', me: b''}
    try:
        while readable:
            ready, _, _ = select.select(readable, [], [], timeout)
            for fd in ready:
                try:
                    data = os.read(fd, 512)
                except OSError as e:
                    if e.errno != errno.EIO:
                        raise
                    # EIO means EOF on some systems
                    readable.remove(fd)
                else:
                    if not data: # EOF
                        readable.remove(fd)
                    result[fd] += data

    finally:
        for fd in [mo, me, mi]:
            os.close(fd)
        if p.poll() is None:
            p.kill()
        p.wait()

    return result[mo], result[me]


ffmpeg_complex_filter = "astats=metadata=1:reset=0.3,ametadata=mode=print:key=lavfi.astats.Overall.Peak_level"
cmd = [
    'ffmpeg',
    '-v',
    '40',
    '-re',
    '-i', 
    'https://icecast.teveo.cu/McW3fLhs',
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
]

out, err = tty_capture(cmd, b"abc\n")
print((out, err))