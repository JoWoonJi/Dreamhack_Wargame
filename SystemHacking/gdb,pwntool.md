**gdb의 명령어 축약**

---

gdb는 훌륭한 명령어 축약 기능을 제공합니다. 어떤 명령어를 특정할 수 있는 최소한의 문자열만 입력하면 자동으로 명령어를 찾아 실행해줍니다. 몇몇 대표적인 명령어들(break, continue, run 등)은 특정할 수 없더라도 우선으로 실행해줍니다. 다음은 자주 사용되는 명령어들의 단축키 예입니다.

- b: break
- c: continue
- r: run
- si: step into
- ni: next instruction
- i: info
- k: kill
- pd: pdisas

---

어떤 함수의 내부까지 궁금할 때는 si를*,* 그렇지 않을 때는 ni를 사용

step into로 함수 내부에 들어가서 필요한 부분을 모두 분석했는데, 함수의 규모가 커서 ni로는 원래 실행 흐름으로 돌아가기 어려울 수 있다. 이럴 때는 **finish**라는 명령어를 사용하여 함수의 끝까지 한 번에 실행

**telescope**은 pwndbg가 제공하는 강력한 메모리 덤프 기능

**vmmap**은 가상 메모리의 레이아웃을 보여준다

요약

- entry: 진입점에 중단점을 설정한 후 실행
- break(b): 중단점 설정
- continue(c): 계속 실행
- disassemble: 디스어셈블 결과 출력
- u, nearpc, pd: 디스어셈블 결과 가독성 좋게 출력
- x: 메모리 조회
- run(r): 프로그램 처음부터 실행
- context: 레지스터, 코드, 스택, 백트레이스의 상태 출력
- nexti(ni): 명령어 실행, 함수 내부로는 들어가지 않음
- stepi(si): 명령어 실행, 함수 내부로 들어감
- telescope(tele): 메모리 조회, 메모리값이 포인터일 경우 재귀적으로 따라가며 모든 메모리값 출력
- vmmap: 메모리 레이아웃 출력

숙

pwntools의 기능

- process & remote: 로컬 프로세스 또는 원격 서버의 서비스를 대상으로 익스플로잇 수행
- send & recv: 데이터 송수신
- packing & unpacking: 정수를 바이트 배열로, 또는 바이트 배열을 정수로 변환
- interactive: 프로세스 또는 서버와 터미널로 직접 통신
- context.arch: 익스플로잇 대상의 아키텍처
- context.log_level: 익스플로잇 과정에서 출력할 정보의 중요도
- ELF: ELF헤더의 여러 중요 정보 수집
- shellcraft: 다양한 셸 코드를 제공
- asm: 어셈블리 코드를 기계어로 어셈블
