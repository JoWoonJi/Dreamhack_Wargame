Use After Free

- **Memory Allocator**: 프로세스의 요청에 따라 동적으로 메모리를 할당 및 해제해주는 주체, 또는 관련된 알고리즘들의 집합. dlmalloc, ptmalloc, jemalloc, tcmalloc 등이 있으며, 리눅스는 그 중에서 ptmalloc2를 사용한다. 구현되는 방식은 다소 차이가 있지만, 핵심 목표는 메모리 단편화의 최소화, 공간 복잡도 및 시간 복잡도의 최적화이다.
- **ptmalloc(pthread memory-allocation)**: dlmalloc을 모태로하는 메모리 할당자. `malloc`, `free`, `realloc` 등을 기반으로 사용자의 동적 메모리 요청을 처리함. 사용하는 주요 객체로는 청크, bins, arena, tcache가 있음.
- **청크(Chunk)**: ptmalloc2가 메모리를 할당하는 단위.
- **bins**: 해제된 청크들을 보관함. ptmalloc은 bin을 이용하여 청크를 빠르게 재할당하고, 단편화를 최소화함. bins에는 fastbin, smallbin, largebin, unsortedbin이 있음.
- **arena**: ptmalloc이 관리하는 메모리들의 정보가 담겨있음. 모든 쓰레드가 공유하는 자원으로, 한 쓰레드가 이를 점유하면 race condition을 막기 위해 lock이 걸림. 병목 현상을 막기 위해 64개까지 생성 가능하지만, 이를 초과할 정도로 많은 연산이 발생하면 병목 현상이 일어남.
- **tcache**: 쓰레드마다 해제된 청크들을 보관하는 저장소. 멀티 쓰레드 환경에서 arena가 가지고 있는 병목 현상의 문제를 일부 해결해줄 수 있음. 쓰레드마다 할당되므로 용량을 고려하여 각 tcache당 7개의 청크만 보관할 수 있음.

//

- **Dangling Pointer**: 해제된 메모리를 가리키고 있는 포인터. UAF가 발생하는 원인이 될 수 있음.
- **Use-After-Free (UAF)**: 해제된 메모리에 접근할 수 있을 때 발생하는 취약점

//

워게임

문제파일 코드를 보면 예제와 비슷하게 

Human과 Robot 구조체는 16 Byte * 3  같은 크기이다.

human_func() 함수와 robot_func() 함수는 메모리 할당 후 초기화하지 않는다.

두 구조체의 크기가 같기 때문에 Human 구조체의 age에 onegadget 주소를 넣고 해제한 후, Robot 구조체를 할당하여 fptr 함수 포인터를 호출하면 UAF 취약점으로 인해 쉘이 뜰 것이다.

robot_func() 함수는 fptr이 null이 아니면 호출을 해주고 있기 때문에 onegadget 실행이 가능하다.

custom_func() 함수는 size의 크기가 0x100 이상이면 메모리를 할당하고 초기화를 하지 않아서 UAF 취약점을 가진다.

libc 파일이 주어졌기에 one_gadget 명령어를 사용해서 oneshot 가젯 오프셋을 구한다

#명령어
one_gadget ./a/libc-2.27.so

oneshot 가젯 오프셋은 0x10a41c이다.

oneshot 가젯은 libc 내부에서 선언된 가젯이기에 주소를 구하려면 libc base addr을 알아야 한다.

UAF 취약점을 활용해 libc base addr을 구해보자.

ptmalloc은 메모리 할당 요청이 발생하면 먼저 해제된 메모리 공간 중에서 같은 크기의 재사용 가능한 공간이 있는지 탐색한다.

ptmalloc에는 free된 청크가 저장되는 128개의 bin이 있는데 이 중 62개는 smallbin, 63개는 largebin, 1개는 unsortedbin, 2개는 사용되지 않는다.

libc base addr을 구하는데 이용되는 것은 unsorted bin이다.

![uaf_overwrite.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/uaf_overwrite.jpg)

플래그 획득.

코드 설명

custom_func()를 4번 실행해서 libc_base를 Leak.
0x500 공간을 2번 할당 1번 해제 -> unsorted bin에 청크가 저장, 1번 재할당 -> 청크 해제.

custom_func()이 할당된 청크 데이터를 출력할 때 재할당 과정에서 user input 값이 덮어씌워진 fd 값이 출력되는데, fd==main_arena addr인 상태에서 user input 데이터를 저장했기 때문이다.

main_arena base address = __malloc_hook + 0x10 이다.

[ unsorted bin fd] = [libc base addr] + [main_arena offset] + [user_input] 즉, 0x3ebc42
user input은 B==0x42

[libc base addr] = [leak addr] - 0x3ebc42 이다.

그렇게 구한 libc base addr에 0x3ebc42를 더해 oneshot 가젯의 주소를 구한다.

그리고 human_func()와 robot_func()를 실행해 UAF 취약점을 발생시켜 fptr 포인터를 oneshot 가젯 주소로 overwrite한 뒤 실행
