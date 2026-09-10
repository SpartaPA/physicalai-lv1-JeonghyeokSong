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
main.cpp:(.text+0x28): undefined reference to `Motor::Motor(unsigned int)'
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

motor.cpp main.cpp

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
0.5 이내 포인트 개수: 3
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

## 1. /turtle1/pose 필드

```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

## 2. ros2 topic hz /turtle_distance 출력

```
average rate: 9.999
	min: 0.099s max: 0.101s std dev: 0.00034s window: 84
average rate: 9.999
	min: 0.099s max: 0.101s std dev: 0.00033s window: 95
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00034s window: 106
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00033s window: 117

```

## 3. 경고 로그
```
[WARN] [1788348962.936525683] [distance_watcher]: Distance 7.84 > 2.50!
```

## 4. 구독자 2개 동시 수신 확인
![alt text](<스크린샷 2026-09-03 16-32-47.png>)

## 5. 정사각형 주행
다각형 가능
![alt text](image-1.png)

## 6. 정상 종료
![alt text](image.png)


# 문제 4.

## 1. colcon build 성공 출력

```
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-assignments/lv1-2/ros2_ws$ colcon build --packages-select turtle_cpp
Starting >>> turtle_cpp
Finished <<< turtle_cpp [5.05s]                     

Summary: 1 package finished [5.25s]
```


## 2. rclpy 발행에서 rclcpp 구독으로 이어진 로그

![alt text](image-2.png)

## 3.

rclcpp, rclpy 에 함수와 클래스가 제공된다.

| | rclpy | rclcpp |
| --- | --- | --- |
| 노드 생성| class 노드이름(Node) | class 노드이름() : public rclcpp::Node |
| 타이머| self.create_timer(주기, 콜백 함수) |this->creat_wall_timer(주기, 콜백 함수) |
| 콜백 | class 내부 함수 | class 내부 public 멤버함수 |
| 종료 | node.destroy(), rclpy.shutdown() |rclcpp::shutdown() |


spin() 루프 진입 -> 이벤트(데이터, 타이머) -> executor(콜백) -> 콜백함수 실행 -> ... -> shutdown()


# 문제 5.

## 1. 호출한 내장 서비스와 타입

클라이언트에서 순서대로 호출한 4개 서비스. 타입은 `ros2 service type <이름>` 으로 확인했다.

| 서비스 | 타입 | 요청 값 | 결과 |
| --- | --- | --- | --- |
| /turtle1/teleport_absolute | turtlesim/srv/TeleportAbsolute | x=6.5, y=5.5, theta=0.0 | 지정 절대 좌표로 순간이동 |
| /turtle1/set_pen | turtlesim/srv/SetPen | r=255, g=0, b=0, width=4, off=0 | 펜을 빨강·굵기 4로 설정 |
| /spawn | turtlesim/srv/Spawn | x=2.0, y=2.0, theta=0.0, name=turtle2 | 새 거북이 이름 반환 |
| /clear | std_srvs/srv/Empty |  | 궤적 삭제 |

teleport·set_pen·spawn 은 turtlesim 전용 타입(`turtlesim/srv/*`)이고, clear 는 요청·응답 필드가 모두 없는 공용 타입 `std_srvs/srv/Empty` 다.


## 2. Service 요청·응답 로그

teleport_absolute x = 6.5 로 이동
```
ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute "{x: 6.5, y: 5.5, theta: 0.0}"
requester: making request: turtlesim.srv.TeleportAbsolute_Request(x=6.5, y=5.5, theta=0.0)

response:
turtlesim.srv.TeleportAbsolute_Response()
```

## 3. 데드락이 생기는 이유

노드 내부 executor(싱글 스레드 - 한번에 하나 실행) 에서 발행, 구독, 서비스 액션의 콜백을 다루는데, executor 가 서비스의 응답을 기다리고 있고 그 서비스는 콜백의 응답을 기다리고 있을때 노드가 멈춰 버린다.

## 4. rotate_absolute 피드백 수신 로그 

```
ros2 run turtle_examples ex05_rotate_absolute_client
[INFO] [1788687276.054480744] [rotate_absolute_client]: goal 전송: theta = 1.571 rad (현재 theta = None)
[INFO] [1788687276.058677480] [rotate_absolute_client]: goal 수락됨 — 피드백 대기
[INFO] [1788687276.059330280] [rotate_absolute_client]: 피드백: remaining = +1.571 rad
[INFO] [1788687276.314981763] [rotate_absolute_client]: 피드백: remaining = +1.315 rad
[INFO] [1788687276.570805230] [rotate_absolute_client]: 피드백: remaining = +1.059 rad
[INFO] [1788687276.827257632] [rotate_absolute_client]: 피드백: remaining = +0.803 rad
[INFO] [1788687277.082700713] [rotate_absolute_client]: 피드백: remaining = +0.547 rad
[INFO] [1788687277.338853340] [rotate_absolute_client]: 피드백: remaining = +0.291 rad
[INFO] [1788687277.594770073] [rotate_absolute_client]: 피드백: remaining = +0.035 rad
[INFO] [1788687277.611733241] [rotate_absolute_client]: 결과 수신: status=SUCCEEDED, delta=-1.552 rad, 현재 theta = 1.5520000457763672
```

## 5. 취소 요청 처리 로그

```
 ros2 run turtle_examples ex05_rotate_absolute_client --theta 0 --cancel-after 1.0
[INFO] [1788688010.187770394] [rotate_absolute_client]: goal 전송: theta = 0.000 rad (현재 theta = None)
[INFO] [1788688010.203020889] [rotate_absolute_client]: 피드백: remaining = -3.136 rad
[INFO] [1788688010.203444016] [rotate_absolute_client]: goal 수락됨 — 피드백 대기
[INFO] [1788688010.459136741] [rotate_absolute_client]: 피드백: remaining = -2.880 rad
[INFO] [1788688010.714585085] [rotate_absolute_client]: 피드백: remaining = -2.624 rad
[INFO] [1788688010.970535866] [rotate_absolute_client]: 피드백: remaining = -2.368 rad
[WARN] [1788688011.204395943] [rotate_absolute_client]: 취소 요청 전송 (요청 시점 theta = 2.128 rad)
[WARN] [1788688011.211161590] [rotate_absolute_client]: 취소 수락됨 (서버가 중단 처리 중). 취소 시점 theta = 2.128 rad
[INFO] [1788688011.212255131] [rotate_absolute_client]: 결과 수신: status=CANCELED, delta=+0.992 rad, 현재 theta = 2.128000020980835
```

## 6. 통신 패턴 설계표

| 기능 | 선택한 모델 | 근거 |
| --- | --- | --- |
| 자세 스트리밍 | Topic | 계속 흐르는 데이터를 여러 구독자에 브로드캐스트, 응답 불필요. |
| 순간이동 | Service | 즉시 끝나는 1회 요청-응답. |
| 펜 색 설정 | Service | 즉시 끝나는 설정 변경 요청-응답. |
| 거북이 추가 | Service | 1회 요청 후 이름을 응답으로 받고 즉시 완료. |
| 목표 각도까지 회전 | Action | 오래 걸리는 작업 + 피드백(remaining) + 취소 필요. |

계속 흐르는 데이터는 Topic,
짧게 끝나는 요청,응답은 Service,
오래 걸리며 피드백,취소가 필요한 작업은 Action.

# 문제 6.

## 1. ros2 interface show turtle_interfaces/msg/WaypointList 출력

```
# 문제 6 — 경유점 목록. "중첩(다른 메시지를 필드로)" 과 "배열" 을 모두 사용합니다.
#
# 다른 패키지의 메시지를 쓸 때는 "패키지/타입" 으로 적습니다 (std_msgs/Header).
# 같은 패키지의 메시지는 패키지 이름 없이 타입 이름만 적어도 됩니다 (Waypoint).
# Waypoint[] 처럼 [] 를 붙이면 가변 길이 배열이 됩니다. (고정 길이는 Waypoint[4])

std_msgs/Header header   # stamp(발행 시각) + frame_id(좌표계 이름, 여기서는 "world")
	builtin_interfaces/Time stamp
		int32 sec
		uint32 nanosec
	string frame_id
Waypoint[] waypoints     # 경유점 배열 — 문제 6 에서는 4개 이상을 채워 발행합니다
	float64 x            # 경유점 x 좌표 [m] (turtlesim 좌표계, 0 ~ 1
	float64 y            #
	float32 tolerance    # 도달 판정 허용 오차 [m] — 이 거리 이내면 "도달" 로 봅
	string  label        #

```

## 2. ros2 topic echo /waypoints 출력 

```
ros2 topic echo /waypoints
header:
  stamp:
    sec: 1788701530
    nanosec: 2251524
  frame_id: world
waypoints:
- x: 2.0
  y: 2.0
  tolerance: 0.30000001192092896
  label: corner_A
- x: 9.0
  y: 2.0
  tolerance: 0.30000001192092896
  label: corner_B
- x: 9.0
  y: 9.0
  tolerance: 0.30000001192092896
  label: corner_C
- x: 2.0
  y: 9.0
  tolerance: 0.30000001192092896
  label: corner_D
---
```

## 3. DrawPolygon 피드백 로그

```
ros2 action send_goal /draw_polygon turtle_interfaces/action/DrawPolygon "{sides: 3, side_length: 2.0}" --feedback
Waiting for an action server to become available...
Sending goal:
     sides: 3
side_length: 2.0

Goal accepted with ID: c9781cda008944dcab7576f99eb1cd80

Feedback:
    completed_sides: 1
progress: 0.3333333432674408

Feedback:
    completed_sides: 2
progress: 0.6666666865348816

Feedback:
    completed_sides: 3
progress: 1.0

Result:
    total_distance: 6.029753619544511

Goal finished with status: SUCCEEDED

```

## 4. 삼각형·오각형·팔각형 궤적 캡처 (이미지 3장)

![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-5.png)

## 5. 액션 취소 처리 결과

```
[INFO] [1788703233.707537550] [polygon_action_server]: 다각형 완성: 총 이동 거리 10.04 m
[INFO] [1788703263.519158583] [polygon_action_server]: goal 수락: sides=8, side_length=2.0
[INFO] [1788703267.891848809] [polygon_action_server]: 변 1/8 완료 (누적 2.01 m)
[INFO] [1788703272.312516957] [polygon_action_server]: 변 2/8 완료 (누적 4.02 m)
[WARN] [1788703272.313003136] [polygon_action_server]: 취소 요청 수신 — 실행 루프에서 즉시 정지합니다
[WARN] [1788703272.364075489] [polygon_action_server]: 취소됨 — 정지. 그때까지 이동 거리 4.02 m

```

## 6. 인터페이스를 별도 패키지로 분리하는 이유

여러 노드가 하나의 인터페이스를 사용할 수 있기 때문에. 노드랑 같이 패키징 된다면 다른 노드들이 인터페이스를 사용 할때 불필요한 패키지에 의존 하게 된다.
# 문제 7. 

## 1. QoS 비호환 시 topic info --verbose 출력

```
ros2 topic info -v /turtle_distance
Type: std_msgs/msg/Float32

Publisher count: 1

Node name: qos_sensor_publisher
Node namespace: /
Topic type: std_msgs/msg/Float32
Endpoint type: PUBLISHER
GID: 01.0f.1d.e2.42.22.2c.26.00.00.00.00.00.00.12.03.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: BEST_EFFORT
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: turtle_distance_subscriber
Node namespace: /
Topic type: std_msgs/msg/Float32
Endpoint type: SUBSCRIPTION
GID: 01.0f.1d.e2.41.26.dc.56.00.00.00.00.00.00.11.04.00.00.00.00.00.00.00.00
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

## 2. 연결되지 않은 원인

`qos_sensor_publisher` -> `Reliability: BEST_EFFORT`
`turtle_distance_subscriber` -> `Reliability: RELIABLE`

구독자를 `--ros-args -p reliability:=best_effort` 로 실행

```
[INFO] [1788738300.444147585] [qos_subscriber]: qos_subscriber 시작: topic=turtle_distance type=Float32 reliability=best_effort durability=volatile depth=10 callback_delay=0.0s
[INFO] [1788738301.528846178] [qos_subscriber]: #1 수신: 7.841
```

## 3. Transient Local 과 Volatile 수신 결과 비교

**Transient Local**
```
[INFO] [1788739255.388249467] [qos_subscriber]: qos_subscriber 시작: topic=waypoints type=WaypointList reliability=reliable durability=transient_local depth=10 callback_delay=0.0s
[INFO] [1788739255.519851757] [qos_subscriber]: #1 WaypointList: 4개 ['corner_A', 'corner_B', 'corner_C', 'corner_D'] frame_id=world
[INFO] [1788739257.380675578] [qos_subscriber]: [통계] 지난 2초 처리 1개 (누적 1개)
[INFO] [1788739259.380743754] [qos_subscriber]: [통계] 지난 2초 처리 0개 (누적 1개) — 0개라면 QoS 비호환이나 발행자 부재를 의심
```

**Volatile**
```
[INFO] [1788739338.867373518] [qos_subscriber]: qos_subscriber 시작: topic=turtle_distance type=Float32 reliability=reliable durability=volatile depth=10 callback_delay=0.0s
[INFO] [1788739340.863367423] [qos_subscriber]: [통계] 지난 2초 처리 0개 (누적 0개) — 0개라면 QoS 비호환이나 발행자 부재를 의심
```

## 4. History depth 1 에서의 메시지 누락 관찰

publisher
- 10.Hz

subscriber
- callback_delay = 0.5

발행은 1초에 10번 구독은 1초에 2번

2/10 = 20% 보존, 80% 누락


```
[INFO] [1788742058.059440747] [qos_subscriber]: qos_subscriber 시작: topic=turtle_distance type=Float32 reliability=reliable durability=volatile depth=1 callback_delay=0.5s
[INFO] [1788742058.095492708] [qos_subscriber]: #1 수신: 7.841
[INFO] [1788742058.596786185] [qos_subscriber]: #2 수신: 7.841
[INFO] [1788742059.100653753] [qos_subscriber]: #3 수신: 7.841
[INFO] [1788742059.602259954] [qos_subscriber]: #4 수신: 7.841
[INFO] [1788742060.103939576] [qos_subscriber]: [통계] 지난 2초 처리 4개 (누적 4개)
[INFO] [1788742060.104398637] [qos_subscriber]: #5 수신: 7.841
[INFO] [1788742060.605826105] [qos_subscriber]: #6 수신: 7.841
[INFO] [1788742061.106782799] [qos_subscriber]: #7 수신: 7.841
[INFO] [1788742061.608339520] [qos_subscriber]: #8 수신: 7.841
[INFO] [1788742062.109894172] [qos_subscriber]: [통계] 지난 2초 처리 4개 (누적 8개)
```

## 5. 토픽 5종 QoS 설계표

설계 기준: **데이터 성격**(연속 스트림 / 일회성 명령 / 설정성 데이터)으로 Reliability·Durability를 정하고, 발행-구독이 요청-제공 호환을 깨지 않도록 맞춘다.

| 토픽 | Reliability | Durability | 근거 |
|---|---|---|---|
| `/turtle1/pose` | BEST_EFFORT | VOLATILE | 거북이 자세를 주기적으로 전송하는 상태 스트림. 한 프레임 놓쳐도 다음 값이 곧 오니 재전송 불필요. 늦게 뜬 노드가 과거 자세를 받을 이유도 없음x |
| `/turtle1/cmd_vel` | RELIABLE | VOLATILE | 구동 명령 — 유실되면 의도한 거동이 어긋날 수 있어 재전송으로 보장. 과거 명령은 무의미하고 그 순간 유효한 명령만 필요 |
| `/waypoints` | RELIABLE | TRANSIENT_LOCAL | 한 번 정하면 계속 유효한 설정. 경유점 하나라도 빠지면 경로가 틀어지므로 RELIABLE, 늦게 합류한 노드도 마지막 목록을 받아함 |
| `/turtle_distance` | BEST_EFFORT | VOLATILE | pose에서 파생한 주기 스트림. 주기적으로 갱신 |
| `/diagnostics` | RELIABLE | VOLATILE | 노드 상태,오류 보고.놓치면 문제 감지를 놓치므로 RELIABLE. 현재 상태 보고라 과거 진단은 필요x |


# 문제 8.

## 1. colcon build 빌드 순서 로그

`colcon list --topological-order`

turtle_py가 turtle_interfaces 에 의존 해야 하기 때문에 먼저 빌드 된다.

```
turtle_cpp	src/turtle_cpp	(ros.ament_cmake)
turtle_interfaces	src/turtle_interfaces	(ros.ament_cmake)
turtle_py	src/turtle_py	(ros.ament_python)
```

## 2. package.xml 의존성 선언 부분

```
  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>turtlesim</depend>
  <depend>std_srvs</depend>
  <depend>turtle_interfaces</depend>
  <depend>action_msgs</depend>
  <depend>rcl_interfaces</depend>
  
  <exec_depend>ros2launch</exec_depend>
```

## 3. setup.py entry_points 

```
entry_points={
        'console_scripts': [
            'distance_publisher = turtle_py.distance_publisher:main',
            'distance_watcher = turtle_py.distance_watcher:main',
            'driver_square = turtle_py.driver_square:main',
            'polygon_action_server = turtle_py.polygon_action_server:main',
            'polygon_action_client = turtle_py.polygon_action_client:main',
            'builtin_service_client = turtle_py.builtin_service_client:main'
        ],
    },
```

## 4. source 전 실행 결과와 source 후 실행 결과

`$AMENT_PREFIX_PATH`
- ros2 가 패키지를 찾는 경로
`$PYTHONPATH`
- 파이선이 모듈을 인식 하는 경로

위 변수들을 `source install/setup.bash` 로 현재 터미널에 install 경로를 추가해 빌드된 패키지를 인식 할 수 있게 한다.



`source install/setup.bash` 전
```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 run turtle_py distance_publisher
Package 'turtle_py' not found
```

`source install/setup.bash` 후
```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ source install/setup.bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 run turtle_py distance_publisher
2026-09-07 11:48:36.965 [RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port9413: open_and_lock_file failed -> Function open_port_internal
[INFO] [1788749317.088649215] [distance_publisher]: [py publisher] distance: 7.84
[INFO] [1788749317.181596395] [distance_publisher]: [py publisher] distance: 7.84
[INFO] [1788749317.281559315] [distance_publisher]: [py publisher] distance: 7.84
```

## 5. src/build/install/log 의 역할

- src: 노드의 로직이 정의되어 있는 소스 코드 파일
- build: 빌드 캐시 데이터
- install: 빌드의 완성본
- log: 빌드 로그

# 문제 9.

## 1. ros2 launch 실행 출력

```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 launch turtle_py turtle_system.launch.py
[INFO] [launch]: All log files can be found below /home/pa2/.ros/log/2026-09-07-13-39-15-268074-pa2-Legion-Pro-5-16IAX10-671814
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [turtlesim_node-1]: process started with pid [671815]
[INFO] [distance_publisher-2]: process started with pid [671817]
[INFO] [distance_watcher-3]: process started with pid [671819]
[INFO] [polygon_action_server-4]: process started with pid [671821]
[turtlesim_node-1] Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway.
[turtlesim_node-1] [INFO] [1788755955.382215010] [turtlesim]: Starting turtlesim with node name /turtlesim  #turtlesim
[turtlesim_node-1] [INFO] [1788755955.384298141] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000] 
[polygon_action_server-4] [INFO] [1788755955.514388795] [polygon_action_server]: polygon_action_server 시작: 액션 /draw_polygon 대기 중 #polygon_action_server
[distance_publisher-2] [INFO] [1788755955.582903638] [distance_publisher]: [py publisher] distance: 7.84 #distance_publisher
[distance_watcher-3] [WARN] [1788755955.594051430] [distance_watcher]: Distance 7.84 > 2.50! #distance_watcher

```

## 2. ros2 node list 결과 — 동시 실행된 노드

```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 node list
/distance_publisher
/distance_watcher
/polygon_action_server
/turtlesim
```

## 3. ros2 param get 으로 확인한 주입 값

```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 param get distance_publisher publish_rate
Double value is: 10.0
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 param get distance_watcher warn_distance
Double value is: 2.5
```

## 4. YAML 값 변경 전후 동작 차이

```yaml
distance_watcher:
  ros__parameters:
    warn_distance: 2.5
```

```bash
[distance_watcher-3] [WARN] [1788758685.640892813] [distance_watcher]: Distance 7.84 > 2.50!
```

```yaml
distance_watcher:
  ros__parameters:
    warn_distance: 5.0
```

```
[distance_watcher-3] [WARN] [1788758511.303079808] [distance_watcher]: Distance 7.84 > 5.00!
```

## 5. 네임스페이스 적용 후 topic list

네임 스페이스 설정
remap으로 연결 한다.
```python
publisher2 = Node(
    package='turtle_py',
    executable='distance_publisher',
    name='distance_publisher',
    namespace='turtle2',
    remappings=[
        ('/turtle1/pose', '/turtle2/pose'),
        ('/turtle_distance', 'turtle_distance'),
    ],
    parameters=[params],
    output='screen',
)
```

네임스페이스 적용 후
node list, ropic list

```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 node list
/distance_publisher
/distance_watcher
/polygon_action_server
/turtle2/distance_publisher
/turtlesim
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws$ ros2 topic list
/parameter_events
/rosout
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose
/turtle2/cmd_vel
/turtle2/color_sensor
/turtle2/pose
/turtle2/turtle_distance
/turtle_distance
```


# 문제 10.

## 1. rqt_graph 캡처

![alt text](image-3.png)

점검 단계:
1. node, topic 존재 유무
2. 실제로 발행 되고 있는지
3. 서로 연결이 되었는지
4. 이름, 타입이 일치 하는지
5. 노드가 잘 짜야져 있는지
  


sim 을 멈춰도 노드의 토픽은 마지막 데이터로 계속 발행된다.
```bash
[INFO] [1788764073.135339849] [distance_publisher]: [py publisher] distance: 9.02
[INFO] [1788764073.235262877] [distance_publisher]: [py publisher] distance: 9.06
[INFO] [1788764073.335357563] [distance_publisher]: [py publisher] distance: 9.10
[INFO] [1788764073.435362018] [distance_publisher]: [py publisher] distance: 9.13
[INFO] [1788764073.535431532] [distance_publisher]: [py publisher] distance: 9.15
[INFO] [1788764073.635443933] [distance_publisher]: [py publisher] distance: 9.17
[INFO] [1788764073.735434816] [distance_publisher]: [py publisher] distance: 9.19
[INFO] [1788764073.836650499] [distance_publisher]: [py publisher] distance: 9.19
[INFO] [1788764073.935472736] [distance_publisher]: [py publisher] distance: 9.19
[INFO] [1788764074.035724956] [distance_publisher]: [py publisher] distance: 9.19
[INFO] [1788764074.135581001] [distance_publisher]: [py publisher] distance: 9.19
[INFO] [1788764074.235541759] [distance_publisher]: [py publisher] distance: 9.19
[INFO] [1788764074.335806939] [distance_publisher]: [py publisher] distance: 9.19
```

hz 도 그에 따라서 계속 측정 되는 모습
```bash
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00105s window: 6271
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00104s window: 6281
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00104s window: 6292
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00104s window: 6303
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00104s window: 6314
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00104s window: 6324
average rate: 10.000
	min: 0.070s max: 0.130s std dev: 0.00104s window: 6334
```

## 2. RViz2 TF + 경유점 마커 캡처

![alt text](image-4.png)

## 3. ros2 bag play 재생 중 구독자 로그

`ros2 run turtle_py distance_watcher`

```
[WARN] [1788772856.520773111] [distance_watcher]: Distance 3.90 > 2.50!
[WARN] [1788772856.620422619] [distance_watcher]: Distance 4.12 > 2.50!
[WARN] [1788772856.720932913] [distance_watcher]: Distance 4.31 > 2.50!
```

`ros2 topic echo /turtle/pose`
```
---
x: 2.5929181575775146
y: 4.255012512207031
theta: 1.055999994277954
linear_velocity: 0.0
angular_velocity: 0.0
---
x: 2.5929181575775146
y: 4.255012512207031
theta: 1.055999994277954
linear_velocity: 0.0
angular_velocity: 0.0
---
x: 2.5929181575775146
y: 4.255012512207031
theta: 1.055999994277954
linear_velocity: 0.0
angular_velocity: 0.0
---
```

## 4. pytest 통과 출력

```bash
colcon test --packages-select turtle_py --pytest-args -k turtle_equation --event-handlers console_direct+
Starting >>> turtle_py
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.10.0, pluggy-0.13.0
cachedir: /home/pa2/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws/build/turtle_py/.pytest_cache
rootdir: /home/pa2/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws/src/turtle_py
plugins: ament-lint-0.12.15, launch-testing-ros-0.19.14, ament-copyright-0.12.15, ament-pep257-0.12.15, launch-testing-1.0.14, ament-flake8-0.12.15, ament-xmllint-0.12.15, cov-3.0.0, colcon-core-0.21.1
collecting ...                          
collected 9 items / 3 deselected / 6 selected                                  

test/test_turtle_equation.py ......                                      [100%]

- generated xml file: /home/pa2/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws/build/turtle_py/pytest.xml -
Finished <<< turtle_py [0.99s]          

Summary: 1 package finished [1.17s]
```

## 5. 함수를 틀리게 바꿨을 때 실패 출력

```bash
colcon test --packages-select turtle_py --pytest-args -k turtle_equation --event-handlers console_direct+
Starting >>> turtle_py
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.10.0, pluggy-0.13.0
cachedir: /home/pa2/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws/build/turtle_py/.pytest_cache
rootdir: /home/pa2/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws/src/turtle_py
plugins: ament-lint-0.12.15, launch-testing-ros-0.19.14, ament-copyright-0.12.15, ament-pep257-0.12.15, launch-testing-1.0.14, ament-flake8-0.12.15, ament-xmllint-0.12.15, cov-3.0.0, colcon-core-0.21.1
collecting ...                          
collected 9 items / 3 deselected / 6 selected                                  

test/test_turtle_equation.py .F....                                      [100%]

__________________________ test_reached[0.3-0.3-True] __________________________
test/test_turtle_equation.py:13: in test_reached
    assert reached(dist, tol) == expected
E   assert False == True
E    +  where False = reached(0.3, 0.3)
- generated xml file: /home/pa2/git/physicalai-lv1-JeonghyeokSong/lv1-2/ros2_ws/build/turtle_py/pytest.xml -
FAILED test/test_turtle_equation.py::test_reached[0.3-0.3-True] - assert Fals...
Finished <<< turtle_py [1.09s]  [ with test failures ]

Summary: 1 package finished [1.50s]
  1 package had test failures: turtle_py
```

## 6. 예외 처리·logging 동작 확인

```bash
ros2 run turtle_py distance_publisher --ros-args -p publish_rate:=0.0
[WARN] [1788776707.665874964] [distance_publisher]: publish_rate must be > 0, setting to default 10.0
```
