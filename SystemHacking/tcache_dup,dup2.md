워게임

 tcache_dup 

double free를 시도 . 에러가 뜨지 않음

ptr[idx]에 "/bin/sh" 넣은다음 free의 plt overwrite
.free의 got 주소 알아낸 다음에 할당.  그곳에 get_shell주소 치환

dfb를 통해서 임의의 주소에 내가 원하는 값을 삽입할 수 있다. (got_overwrite)

![tcache_dup.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/tcache_dup.jpg)

플래그 획득

//

tcache_dup2

Partial RELRO가 적용돼있으니 tcache_dup과 마찬가지로 GOT overwrite 공격

코드 분석
(1) create_heap: size를 입력받아 size 크기만큼의 청크를 할당해주고, 할당한 청크의 주소를 ptr[idx]에 담는다.
그 후, data를 입력받아 입력받은 data를 해당 chunk에 저장한다. 그리고 idx를 1 증가시킨다

(2) modify_heap: idx와 size를 입력받는다. 그 후 사용자에게서 data 값을 size만큼 입력받아 ptr[idx]의 값을 입력값으로 수정한다.
이때, size가 0x10보다 크다면 프로그램이 종료된다.

(3) delete_heap: 사용자에게서 idx를 입력받아 ptr[idx]를 free 한다.
이때, free한 후, ptr[idx]를 초기화 시켜주지 않으므로, Dangling Pointer가 발생하고, 이를 통해 Double Free Bug 취약점이 발생한다.

1. double free bug를 이용해 tcache에 duplicated free list를 만든다
2. puts_got에 청크를 할당하고 puts_got를 get_shell()의 주소로 overwrite 하여 shell을 획득
- *tcache count에 유의. tcache count == 0이라면 chunk를 할당해줄 때 tcache를 참조하지 않기 때문.

![tcache_dup2.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/tcache_dup2.jpg)

플래그 획득
