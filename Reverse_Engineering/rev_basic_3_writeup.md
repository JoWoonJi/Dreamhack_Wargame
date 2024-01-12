드림핵 reverse engineering의 마지막 워게임. 예제 없는 실전!

ctf에 참가했다고 생각하고 풀어보자

1.

![rev_basic_3-1.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/38552da6-340d-42c1-a9a1-b181ff331f03/a469487d-31d2-4b82-9dca-b15f1418efb2/rev_basic_3-1.jpg)

그동안 배워왔던 ida의 F5기능(디컴파일,어셈블리어를 프로그래밍언어처럼 이해하기 쉽게만들어주는)을 활용해서 main함수를 보면 sub_7FF6C25C11B0는 input 기능, sub_7FF6C25C1210는 scanf기능, 

sub_7FF6C25C1000 함수가 무언가를 비교해서 correct ,wrong을 결정 짓는 함수 임을 알 수 있다. 

sub_7FF6C25C1000 함수를 분석해보자.

2.

![rev_basic_3-2.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/38552da6-340d-42c1-a9a1-b181ff331f03/2e8fe96f-bc08-4918-b0ef-4bbed6f94b71/rev_basic_3-2.jpg)

마찬가지로 수도코드 기능을 활용해서 sub_7FF6C25C1000를 살펴보면 byte_7FF6C25C3000변수가 옆에 있는 문자열과 비교하는 핵심 변수임을 알 수 있다. 

3.

![rev_basic_3-3.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/38552da6-340d-42c1-a9a1-b181ff331f03/45d7d50b-e960-4dd0-9509-4e4cc61fac57/rev_basic_3-3.jpg)

byte_7FF6C25C3000 살펴보면 db(define byte) 바이트크기의 데이터 값이 나열되어있는것으로 보아 

이 값들을 참조해서 sub_7FF6C25C1000 함수가 비교 연산을 하는 것을 알 수 있다. 

어떤 값인지 파이썬으로 실행해보자.

4.

파이썬으로 디코딩

```python
def decode_chars(chars):
    return ''.join(chr((char - (2 * i)) ^ i) for i, char in enumerate(chars))

chars = [0x49, 0x60, 0x67, 0x74, 0x63, 0x67, 0x42, 0x66, 0x80, 0x78,
         0x69, 0x69, 0x7B, 0x99, 0x6D, 0x88, 0x68, 0x94, 0x9F, 0x8D,
         0x4D, 0xA5, 0x9D, 0x45]

decoded_string = decode_chars(chars)
print(decoded_string)
```

![rev_basic_3-4_code.jpg](https://prod-files-secure.s3.us-west-2.amazonaws.com/38552da6-340d-42c1-a9a1-b181ff331f03/4dc12873-1034-425c-9db6-2fae5eff87b2/rev_basic_3-4_code.jpg)

I_am_X0_xo_Xor_eXcit1ng 이 출력된다. 플래그 획득.
