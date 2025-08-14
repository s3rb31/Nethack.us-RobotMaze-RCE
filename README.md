# Nethack.us-RobotMaze-RCE

The main file you need to look at is 'solve_maze.py'

## What the script actually does

This is an **automated maze-solver + buffer overflow exploit**.

It connects to a remote server, completes a mini-game (maze), then uses a vulnerability (likely in how the server processes input) to inject shellcode.

The shellcode will then start a reverse shell and connect back to the attacker.

Once exploited, the attacker gains **remote command execution** on the target.
