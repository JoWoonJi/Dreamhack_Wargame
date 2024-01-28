- **tcache_entry**: 해제된 tcache 청크를 나타내는 구조체. 각 청크는 `next`라는 멤버 변수로 연결됨. Double free 보호 기법이 적용되면서, `key`라는 멤버 변수가 추가됨.
- **tcache_perthread_struct**: tcache를 처음 사용하면 할당되는 구조체.
- **Double Free Bug**: 한 청크를 두 번 해제할 수 있는 버그.
- **Tcache Duplication:** tcache에 같은 청크가 두 번 연결되는 것. double free bug로 발생시킬 수 있으며, tcache poisoning으로 응용될 수 있음.

- **Tcache Dup**: Double free 등을 이용하여 tcache에 같은 청크를 두 번 이상 연결시키는 기법.
- **Tcache Poisoning**: tcache에 원하는 주소를 추가하여 해당 주소에 청크를 할당시키는 기법. 임의 주소 읽기, 임의 주소 쓰기의 수단으로 사용될 수 있다.

//

○ tcache poisoning
Double Free Bug를 이용하여tcache_entry를 조작해서 이미 할당된 메모리에 다시 힙 청크를 할당하는 공격 기법이다. tcache에서 사용하는tcache_put과tcache_get함수에서는 old와 p를 검증하지 않기 때문에 한 개의 청크를 연속으로 해제할 수 있다. (참고로 GLIBC 2.26과 2.29 이상의 버전에서는 DFB를 검증하는 로직이 추가됐다.)

tcache poisoning을 이해하기 위해서는 청크 개념을 알아야한다.

왼쪽은 alloc 청크, 오른쪽은 free 청크다. 차이점을 보면 alloc 청크에서는 data를 담는 부분이 free 청크에서는 fd, bk를 담는다. 여기서 생각해볼 지점은 “만약 A 청크가 alloc 청크인지 free 청크인지 구분없이 중첩된 상태라면 어떻게 될 것인가?”이다.

똑같은 메모리를 2번 해제한다고 가정하자.

tcache_entry를 확인하면 자기 자신을 next 포인터로 가리키는 것을 확인할 수 있다.

즉, tcache Duplication이 발생했다.
→ 청크는중첩상태가 된다.

이전과 같은 크기로 힙을 할당하고 데이터로 [임의의 주소]를 입력하면 어떻게 될까?
→ next 포인터가 [임의의 주소]로 바뀐다.

할당 과정임에도0x1edb260주소가 청크로부터 할당되는 것이 아니라 오히려 next 포인터에 [임의의 주소]가 연결됐다.

DFB에 의해 청크가 중첩 상태였기 때문에 할당을 했음에도 해제한 것과 같은 결과가 도출된 것이다.

이와 같이 tcache에 저장된 주소를 조작하는 공격을 "Tcache Poisoning"이라고 한다.

워게임

예제대로 진행 

코드 분석
case 1) size만큼 메모리 공간을 할당하고 데이터를 저장
→ 주소는*chunk변수에 저장
case 2) chunk 해제
case 3) chunk가 가리키는 데이터를 출력
case 4) chunk가 가리키는 메모리 공간을 원하는 데이터로 수정

요약하면malloc,free,modify,output4가지 기능을 수행할 수 있는 프로그램이다.

4가지를 모두 수행할 수 있으므로tcache_dup취약점을 이용한 exploit이 가능하다

hook overwrite로 쉘을 획득해야한다.

Tcache Poisoning을 이용해__free_hook을 oneshot 가젯으로 덮는 방식을 생각할 수 있다.

똑같은 크기로 할당/해제하는 과정을 거쳐서 tcache entry에 stdout 주소가 포함되도록 조작하는 과정이다. tcache entry를 조작하고 "dreamhack"을 할당하여 tcache entry가 stdout주소를 가리키게 한 상태로 case 3을 이용해서 출력하면 stdout 주소를 얻을 수 있다.

참고로 edit()는 DFB mitigation을 우회하기위해 추가한 코드로 e→key을 덮는 역할

stdout 주소를 얻으면 위와 같이 stdout offset과 연산해서 libc_base 주소를 얻을 수 있다.

libc_base 주소를 얻었다면 __free_hook과 oneshot gadget 주소까지 구할 수 있다.

다음으로 __free_hook()을 oneshot 가젯으로 덮자.

libc_base를 leak 할 때처럼 tcache 검증을 우회하는 동시에 overwrite까지 수행

__free_hook()을 oneshot 가젯으로 덮고free()를 호출한다면?
→__free_hook() == oneshot_gadget이 실행되면서 쉘을 획득

![Tcache_poisoning.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/Tcache_poisoning.jpg)

플래그 획득
