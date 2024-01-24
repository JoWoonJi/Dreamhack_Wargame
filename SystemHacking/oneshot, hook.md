ONESHOT

코드를 보면 C언어 라이브러리에 소속된 stdout 요소의 메모리 주소를 제공해주고, read() 함수를 통해 msg라는 입력 버퍼에 사용자 입력을 받는다. 근데 원래 msg의 길이는 16바이트이지만, read()에서는 46바이트만큼을 덮고 있다. 따라서 버퍼 오버플로우 취약점이 발생하며, 이를 이용해 RET overwrite를 실시하여 one-gadget의 주소로 return address를 덮어버리면 된다.

return 0; 이 실행될 때 one-gadget의 주소로 변조된 return 이 이루어져 셸이 획득. 다만 이때 중간에 check라는 변수 값이 0을 초과하면 프로그램을 도중해 중단시키기 때문에, check 변수가 실제 스택 프레임에서 어느 위치에 존재하는지를 살펴서, 이 검사하는 부분을 우회시키고 RET overwrite를 수행

stdout의 절대 주소를 받고, 이를 통해 stdout의 오프셋을 stdout의 절대 주소로부터 뺌으로써 주어진 라이브러리의 절대 주소를 계산, 그 뒤 적절한 one gadget의 절대 주소를 다시 원래 라이브러리 절대 주소에 더해 계산. 0x45226 오프셋에 있는 one gadget을 사용

원 가젯의 주소까지 알았다면, 중간에 check 변수가 0을 초과하는지 검사하는 부분만 신경써서 오버플로우를 일으키고, return address를 one gadget 주소로 덮어버리면, 프로그램이 종료될때 실행 흐름이 셸을 실행시키는 one gadget으로 바뀌면서 셸이 획득

![oneshot.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/oneshot.jpg)

플래그 획득 

//

HOOK

구조는 이전 워게임 oneshot과 비슷.

stdout의 절대 메모리 주소를 알려준다. → 해당 바이너리가 사용하는 라이브러리(libc)의 절대 주소를 오프셋을 통해 계산하여 알아낼 수 있다.

입력에 앞서 먼저 입력의 크기를 받는다

해당 크기만큼을 메모리에서 동적 할당(malloc)을 통해 받는다

이어 동적 할당된 그 공간(*ptr)에 데이터를 이전에 말한 크기만큼 입력받는다

- (long *)*ptr = *(ptr+1);

free() 함수로 주어진 공간을 해제한다

우선 구조를 보면 free() 함수를 통해 같은 대상(ptr)을 두 번 할당 해제하려고 하여, double free 버그(취약점)이 발생하고, 그 뒤에 system("/bin/sh")을 실행. 일반적으로 이미 할당 해제한 메모리 영역을 다시 또 하려고 하면 불법적인 메모리 접근 시도로 간주되기 때문에 segmentation fault가 발생. 따라서 runtime error가 발생할 것이 거의 확실하므로 system("/bin/sh")가 실행되기 어렵다.

문제 제목에 맞게, hook overwrite를 사용. 현재 문제는 hook overwrite를 허용하는 취약한 버전의 라이브러리 파일을 사용하고 있으며, stdout의 절대 주소를 알기 때문에 이를 통해 라이브러리의 시작 절대 주소를 구하는 방식으로 __free_hook 주소를 구할 수 있다. (free()함수가 소스코드에서 사용되고 있기 때문에 이용이 가능)

이 __free_hook, 즉 free hook overwriting을 위해 free()함수에 인자를 호출해주어야 하는데, free() 함수에 system("/bin/sh")과 같은 셸을 획득시키는 one gadget을 __free_hook에 쓰던가 전달하는 방향으로 셸이 획득되도록 하면 된다. 이게 가능한 이유는 바로 아래의 C언어 포인터 연산 코드 때문

- (long *)*ptr =*(ptr+1);

위 코드는 ptr에서 sizeof(long) 만큼 1번 떨어진 공간에 있는 데이터를 ptr이 가리키고 있는 값(그러나, 그 크기를 8바이트(long *)로 함. 즉, 8바이트가 넘는 데이터는 옮기지 않음.)이 다시 가리키고 있는 값에 대입하는 것과 같다.

이번 소스코드에 나오는 free() 함수가 가지고 있는 __free_hook과 one gadget의 주소가 있다고 할 때, *ptr에 __free_hook이 들어있고, *(ptr + 1)에 one gadget이 들어있으면(또는 ptr에 __free_hook의 주소, (ptr + 1)에 one gadget의 주소), 아래와 같이 one gadget의 주소가 __free_hook이 가리키는 값이 되어 결과적으로 free hook overwrite가 되기 때문

이렇게 되면, __free_hook 이 사용되는 취약한 라이브러리를 사용하는 프로그램(마치 이 워게임 문제와 같은)은 free() 함수가 실행될때 __free_hook에 값이 있는 것을 감지, 이쪽으로 실행 방향을 돌리다가 one gadget이 실행되어 두번째 free()가 실행되기 전에 이미 셸이 실행

stdout 절대 주소를 알려줄때 libc의 절대 주소를 구하고, 미리 구해놓은 원 가젯의 오프셋을 구해 원 가젯을 마련하고, 동시에 __free_hook의 절대 주소를 구해놓는다. 이어 ptr에 순서대로 __free_hook의 절대 주소와 원 가젯의 절대 주소를 넣으면 된다.

![hook.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/hook.jpg)

플래그 획득
