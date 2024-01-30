- **Type Overflow** : 변수가 저장할 수 있는 최댓값을 넘어서서 최솟값이 되는 버그
- **Type Underflow** : 변수가 저장할 수 있는 최솟값보다 작아 최댓값이 되는 버그
- **Most Significant Bit (MSB)** : 데이터의 최상위 비트, 부호를 표현하기 위해 사용됨|

// 

워게임 sint

get_shell 함수를 실행하는 것이 목표

size를 입력받고, size-1만큼 buf를 read한다.

여기서 size는 0이상 255이하여야만 한다.

read의 3번째 인자는 unsigned int이기 때문에 무조건 0 또는 자연수이다.

따라서 size를 0으로 준다면 -1이 unsigned int에서 엄청나게 큰 자연수로 바뀔 것이다.

디스어셈블 결과 buf의 위치는 [ebp-0x100]이므로 RET과 0x104만큼 차이가 난다.

카나리도 없으므로 buffer overflow를 일으킨다.

![sint.jpg](https://github.com/JoWoonJi/Dreamhack_Wargame/blob/main/SystemHacking/img/sint.jpg)

플래그 획득
