**Calling Convention**

**x86 함수 호출 규약**

| 함수호출규약 | 사용 컴파일러 | 인자 전달 방식 | 스택 정리 | 적용 |
| --- | --- | --- | --- | --- |
| stdcall | MSVC | Stack | Callee | WINAPI |
| cdecl | GCC, MSVC | Stack | Caller | 일반 함수 |
| fastcall | MSVC | ECX, EDX | Callee | 최적화된 함수 |
| thiscall | MSVC | ECX(인스턴스), Stack(인자) | Callee | 클래스의 함수 |

**x86-64 함수 호출 규약**

| 함수호출규약 | 사용 컴파일러 | 인자 전달 방식 | 스택 정리 | 적용 |
| --- | --- | --- | --- | --- |
| MS ABI | MSVC | RCX, RDX, R8, R9 | Caller | 일반 함수, Windows Syscall |
| System ABI | GCC | RDI, RSI, RDX, RCX, R8, R9, XMM0–7 | Caller | 일반 함수 |

$ ulimit -c unlimited

![ReturnAddressOverwrite.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/38552da6-340d-42c1-a9a1-b181ff331f03/e333012a-3c22-474e-a822-92f029fda8db/ReturnAddressOverwrite.jpg)

핵심은 페이로드에 A(더미값) * 56 (10진수는56, 16진수 0x38) 만큼 채워주고 그 뒤에 get shell의 주소 값을 넣어주는 것이다.  (버퍼 오버플로우)

shell의 주소 반환값은 리틀엔디언으로. 리틀엔디언은 역순이고 빅엔디언은 그대로 들어간다고 생각하면 됨. 0x12345678 이면 리틀엔디언은 거꾸로 78 56 34 12 이렇게 들어간다.

그래서 원래의 쉘주소는 0x (00 00 00 00 00 40 06 aa) 였던것.

쉘주소는 pwndbg로. print get_shell

파이썬 코드를 실행 하면 쉘을 획득하게 되고 ls 명령어로 파일명을 알아내고 flag를 cat으로 읽으면 된다. 

DH 획득.
