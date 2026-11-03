"""Unprivileged stdio-to-local-socket bridge; no lab implementation or data mounted here."""
import socket
import sys
import threading

sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
sock.connect(sys.argv[1])


def outgoing():
    for line in sys.stdin.buffer:
        sock.sendall(line)
    sock.shutdown(socket.SHUT_WR)


thread=threading.Thread(target=outgoing,daemon=True)
thread.start()
while True:
    chunk=sock.recv(65536)
    if not chunk:break
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
