# 문제 1.

## 1. 수동 2단계 빌드 명령 (터미널 입력)
```
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-assignments/lv1-2/cpp_basics$ g++ -Wall -std=c++17 stop_distance.cpp -o stop_distance
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-assignments/lv1-2/cpp_basics$ ./stop_distance 
속도: 10
마찰: 2

5.09858
```

## 2. undefined reference 에러 메시지 (출력) — 컴파일 에러와의 차이 설명

컴파일은 되었지만 main안에 motor.hpp 선언만 있고 정의 부분이 motor.cpp 로 링크 되어야 하지만 그 파일을 지정 하지 않았기 때문에 undefined refernce 정의 되지 않음 에러가 난다.

```
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-assignments/lv1-2/cpp_basics$ g++ main.o -o main
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x28): undefined reference to `Motor::Motor(int)'
collect2: error: ld returned 1 exit status
```

## 3. CMake 빌드 출력


```
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-assignments/lv1-2/cpp_basics/build$ make
Consolidate compiler generated dependencies of target main
[ 33%] Building CXX object CMakeFiles/main.dir/main.cpp.o
[ 66%] Building CXX object CMakeFiles/main.dir/motor.cpp.o
[100%] Linking CXX executable main
[100%] Built target main
```

## 4. 증분 빌드 시 재컴파일된 파일

motor.cp,p main.cpp

motor.cpp 만 수정 했지만 main.cpp 도 motor 를 참조 하고있기 때문에 재 컴파일 되었다. 증분 빌드의 단위는 소스파일.cpp 가 아니라 의존 하는 모든 파일이다.

# 문제 2.

## 1. 다형성 루프 출력

```
Lidar data would be here...
Imu data would be here...
```

## 2. 스택 객체와 힙 객체의 소멸 시점

종료 또는 블록 나오면 선언의 역순으로 정리됨. 클래스 내부에서는 종속의 역순으로 정리된다.

```
Lidar data would be here...
Imu data would be here...
~Lidar
~Sensor
~Imu
~Sensor
```

## 3. 가상 소멸자를 뺐을 때의 차이

가상 소멸자를 제거 했을때,
출력 안함.
```
Lidar data would be here...
Imu data would be here...
```
virtual 타입만 제거 했을때,
상속 받은 클래스 들은 소멸자 호출 안됨.
```
Lidar data would be here...
Imu data would be here...
~Sensor
~Sensor
```

## 4. `count_if` 결과

```
최근 lidar 측정값0.1, 0.2
최근 imu 측정값0.3, 0.4
0.5 이내 포인트 개수: 2
```

## 5. 누수 검출 결과

**fsanitize=address**
SUMMARY: 루프로 돌린 10개의 오브젝트 검출 new_delete 

```
=================================================================
==35687==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 240 byte(s) in 10 object(s) allocated from:
    #0 0x7d36a0eb61e7 in operator new(unsigned long) ../../../../src/libsanitizer/asan/asan_new_delete.cpp:99
    #1 0x59b84b741b0d in main /home/sjh/git/physicalai-lv1-assignments/lv1-2/cpp_basics/sensors/main.cpp:105
    #2 0x7d36a0629d8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58

SUMMARY: AddressSanitizer: 240 byte(s) leaked in 10 allocation(s).
```

수정 후 소멸자 전부 호출됨
```
./main_asan 
Lidar data would be here...
Imu data would be here...
최근 lidar 측정값0.1, 0.2
최근 imu 측정값0.3, 0.4
0.5 이내 포인트 개수: 3
clamp speed: 5
clamp pixel: 100
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Lidar
~Sensor
~Imu
~Sensor
```

**valgrind**
검출: in use at exit: 240 bytes in 10 blocks
```
==36999== HEAP SUMMARY:
==36999==     in use at exit: 240 bytes in 10 blocks
==36999==   total heap usage: 21 allocs, 11 frees, 74,400 bytes allocated
==36999== 
==36999== 240 bytes in 10 blocks are definitelylost in loss record 1 of 1
==36999==    at 0x4849013: operator new(unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
==36999==    by 0x10AE43: main (in /home/sjh/git/physicalai-lv1-assignments/lv1-2/cpp_basics/sensors/main)
==36999== 
==36999== LEAK SUMMARY:
==36999==    definitely lost: 240 bytes in 10 blocks
==36999==    indirectly lost: 0 bytes in 0 blocks
==36999==      possibly lost: 0 bytes in 0 blocks
==36999==    still reachable: 0 bytes in 0 blocks
==36999==         suppressed: 0 bytes in 0 blocks
==36999== 
==36999== For lists of detected and suppressed errors, rerun with: -s
==36999== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 0 from 0)
```

std::make_unique 사용
```
==37257== HEAP SUMMARY:
==37257==     in use at exit: 0 bytes in 0 blocks
==37257==   total heap usage: 21 allocs, 21 frees, 74,400 bytes allocated
==37257== 
==37257== All heap blocks were freed -- no leaks are possible
==37257== 
==37257== For lists of detected and suppressed errors, rerun with: -s
==37257== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

# 문제 3.

## /turtle1/pose 필드

```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```