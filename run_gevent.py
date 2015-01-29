from gevent import monkey; monkey.patch_os()
import sys
import getopt
from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer
from cplatform.wsgi import application
from multiprocessing import Process

addr, port = '127.0.0.1', 8000
opts, _ = getopt.getopt(sys.argv[1:], "b:")
for opt, value in opts:
    if opt == '-b':
        addr, port = value.split(":")
server = WSGIServer((addr, int(port)), application)


 
process_count = 4
 
for i in range(process_count - 1):
    Process(target=server.serve_forever(), args=tuple()).start()








 

