import sys
from subprocess import PIPE, Popen
from threading  import Thread
from queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

p = Popen(['ping 8.8.8.8'], stdout=PIPE)
q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True
t.start()


print('Im half way')

try:
    line = q.get_nowait()
except Empty:
    print('no output yet')
else: # got line
    print('hehe')