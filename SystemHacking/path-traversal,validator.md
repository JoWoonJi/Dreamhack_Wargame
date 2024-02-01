# path traversal , validator

- **절대 경로(Absolute Path):** 루트 디렉터리에서 접근할 파일 및 디렉터리 위치까지 모두 표현하는 방식
- **상대 경로(Relative Path):** 현재 사용자의 위치를 기준으로 다른 파일이나 디렉터리의 경로를 표현하는 방식.
- **Path Traversal:** 경로 문자열에 대한 검사가 미흡하여 허용되지 않는 경로에 접근할 수 있는 취약점

## 시스템 해킹 마지막 워게임!

# validator

문제 파일 두개 validator_dist와 validator_server을 checksec 해보면 

기본으로 제공하는 `ASLR`을 제외한 `Canary`, `NX`, `PIE`가 모두 비활성화되어 있고, `Partial RELRO`가 적용되어 있으므로 GOT overwrite가 가능하다

validator_dist를 디버깅해보면 이 바이너리의 main에서 `read()`를 호출하는데, 버퍼의 위치는 `rbp-0x80`이고 readable size는 `0x400`으로 stdin으로부터 읽는다. 이때 버퍼의 위치 `rbp-0x80`에서부터 `0x400`만큼 readable하므로 **`Stack Buffer Overflow`**취약점이 존재한다.

디버깅하며 확인했듯이 readable한 최대 크기는 0x400으로 **stack buffer overflow**가 가능하다. 그러나 return address를 `one_gadget`으로 덮으려면 라이브러리의 매핑 주소를 구해야 하므로 복잡하다. 따라서 **Return Oriented Programming**으로 exploit를 진행한다.

- 특정 함수의 GOT에 shellcode 주입
- 그 함수의 plt로 return
    
    > GOT에 shellcode를 주입해서 exploit가 가능한 이유는, 문제의 힌트로 주어져 있듯이 v5.4.0 이전 커널에서는 NX가 비활성화돼 있으면 읽기 권한이 있는 데이터 영역이 실행 가능하기 때문이다.
    > 

- return address를 gadget으로 overwrite하기 위해서 0x87번째까지 dummy로 덮는다
- 0x88번째부터 ROP payload를 구성한다.

shellcode로 덮어 쓸 GOT이 3개가 있다. 이 중 `memset`의 GOT를 이용

ROP로 read를 호출하여 memset의 GOT에 shellcode를 저장한다. 그리고 memset의 GOT으로 return하여 shellcode를 실행

shellcode를 nasm으로 assemble

nasm -f elf64 shellcode.asm

objdump -d shellcode.o

![validator.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/validator.jpg)

플래그 획득!
