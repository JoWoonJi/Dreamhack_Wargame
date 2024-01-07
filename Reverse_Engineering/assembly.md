| 명령 코드 |  |
| --- | --- |
| 데이터 이동(Data Transfer) | mov, lea |
| 산술 연산(Arithmetic) | inc, dec, add, sub |
| 논리 연산(Logical) | and, or, xor, not |
| 비교(Comparison) | cmp, test |
| 분기(Branch) | jmp, je, jg |
| 스택(Stack) | push, pop |
| 프로시져(Procedure) | call, ret, leave |
| 시스템 콜(System call) | syscall |

//

w d q 2 4 8 바이트 

//

| mov dst, src : src에 들어있는 값을 dst에 대입 |  |
| --- | --- |
| mov rdi, rsi | rsi의 값을 rdi에 대입 |
| mov QWORD PTR[rdi], rsi | rsi의 값을 rdi가 가리키는 주소에 대입 |
| mov QWORD PTR[rdi+8*rcx], rsi | rsi의 값을 rdi+8*rcx가 가리키는 주소에 대입 |

| lea dst, src : src의 유효 주소(Effective Address, EA)를 dst에 저장합니다 |  |
| --- | --- |
| lea rsi, [rbx+8*rcx] | rbx+8*rcx 를 rsi에 대입 |

뒤에서 앞으로

//

cmp는 두 피연산자를 빼서 대소를 비교합니다.

test는 두 피연산자에 AND 비트연산을 취합니다

****jmp addr: addr로 rip를 이동시킵니다.****

****je addr: 직전에 비교한 두 피연산자가 같으면 점프 (jump if equal)****

****jg addr: 직전에 비교한 두 연산자 중 전자가 더 크면 점프 (jump if greater)****

//

**push val : val을 스택 최상단에 쌓음**

**pop reg : 스택 최상단의 값을 꺼내서 reg에 대입**

**call addr : addr에 위치한 프로시져 호출**

**leave: 스택프레임 정리**

**ret : return address로 반환**
