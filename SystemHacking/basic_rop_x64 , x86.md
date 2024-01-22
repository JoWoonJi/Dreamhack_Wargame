
basic_rop_x64

1. checksec 명령어로 문제파일에 어떤 보호기법이 걸려있는지 확인
- no canary, no pie / NX enabled

1. 소스코드 확인하여 취약점 찾기

buf값이 0x40 , read함수 0x400 버퍼오버플로우 취약점 발견

3.필요한 가젯을 구한다. ROPgadget —binary basic_rop_x64 | grep ‘pop rdi’ 등등

1. payload를 구성한다

'\x90'으로 48만큼 ret주소 전까지 채워주고 pop rdi가젯으로 read_got를 넣어주고 puts_plt로 read_got를 출력하게 된다. 이후 다시 메인 주소로 리턴해줘서 system의 실제 주소를 구해서 페이로드를 재구성

p.recv(40)으로 write sizeof(buf)만큼 받은 다음 read@got주소를 구해주고 leak된 주소를 read offset을 빼준 뒤 나온 베이스 주소를 이용해서 system함수의 실제 주소를 구해준다. 이후 libc에서 /bin/sh를 찾고 base를 더해주면 실제 주소가 

다시 리턴주소까지 0x48만큼의 크기를 채워주고 ret가젯을 이용해서 스택 정렬을 맞춰준 뒤 pop rdi 가젯으로 binsh를 넣어주고 system함수로 리턴해주면 쉘을 획득

![basic_rop_x64.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/basic_rop_x64.jpg)

플래그 획득

//

basic_rop_x86

x64할때와 비슷한과정

![basic_rop_x86.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/basic_rop_x86.jpg)

플래그 획득
