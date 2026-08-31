# 문제 1

## 1. 배달 로봇의 연산 분담과 실시간성 설계

| 부품       | 주기         | 지연 예산   | 초당 데이터 크기         | 데이터 타입                    | 비고                                 |
| -------- | ---------- | ------- | ----------------- | ------------------------- | ---------------------------------- |
| 2D Lidar | 8hz        | 125ms   | 0.257mbps         | sensor_msgs/LaserScan     | float32 / 초당 8000 샘플               |
| 카메라      | 1080p30fps | 33.33ms | 622mbps, 1492mbps | sensor_msgs/Image.msg     | flfoat32 / raw(10bit), RGB         |
| IMU      | 100hz      | 10ms    | 0.2368mbps        | sensor_msgs/Imu.msg       | float 64 / 각속도, 선속도, 쿼터니언 (공분산 포함) |
| encoder  | 1khz       | 1ms     | 0.768mbps         | sensor_msg/JointState.msg | 4륜                                 |
| LTE      |            | 30ms    |                   |                           | 하향 150mbps/ 상향 50mbps              |



## 1. 연산 분담 배치표
| 작업           | 위치   | 지연 예산 | 초당 데이터량 입/출력                              | 근거                                                                                                                      |
| ------------ | ---- | ----- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 모터 속도 제어     | 임베디드 | 1ms   | 32kbps\*4                                 | 4륜, 입력은 로봇 상태값 을 받아 목표 속도 값 출력. 다른 통신 예산은 필요 x                                                                          |
| 장애물 감지       | edge | 125ms | 0.256mbps/ 8bps 장애물 있을때+ 0.256kbps        | Lidar 에서 raw 샘플링 결과를 받아와서 유효 장애물 판단, 장애물 있으면 (거리,각도) 추가. 지연예산은 라이다 센서 스캔 주기를 따라감.                                       |
| 보행자 인식       | edge | 33ms  | 1424mbps + 32bps/ 8bps 보행자 있을때 + 1.95kbps | 데이터 량이 커서 전처리된 데이터만 edge로 받아 처리하는것이 나을것 같다. 또한 회피는 네트위크가 끊겨도 제어 되어야 하기 때문에. 출력은 보행자 인식 상태와 거리,각도                        |
| 위치 파악        | edge | 10ms  | 1.0048mbps/ 9.6kbps                       | encoder + IMU의 각속도, 선속도 로 추론 하여 위치를 파악 한다. 출력값은 Vector3 (float32, float32,float32)                                      |
| 지도 기반 경로 계획  | 클라우드 | 30ms  | 5.33kbps/ 2.13kbps                        | 위치파악(x,y,theta) + 목표 지점Vector2  -> 추론(클라우드) -> 각속도, 선속도                                                                 |
| 배달 완료 사진 업로드 | 클라우드 | 1s    | 6MB                                       | RGB 1프레임,  49.733 mbps  < LTE 상향, edge 에서 크롭 하거나 압축 필요                                                                  |
| 운행 로그 집계     | 클라우드 | 1s    | 0.256kbps                                 | 위치(x,y,theta 12byte) + 속도(각속도,선속도 8byte) + 배터리(4byte) + 타임스탬프(8byte) = 32byte(256bit), 1Hz로 전송 → 256bit×1Hz = 0.256kbps |
|              |      |       |                                           |                                                                                                                         |


## 2. 카메라 원시 영상 전송량

초당 전송 되는,
카메라 raw 데이퍼 크기 622/8 = 77.75MB/s
상향 데이터 크기 50/8 = 6.25MB
- 10배 이상 초과 
- 6MB 이하의 데이터로 가공 필요

## 3. 인지·판단·제어 계층 매핑과 주기표

|     |                                        |
| --- | -------------------------------------- |
| 인지  | 장애물, 보행자, 신호등, 목적지, 음식, 배달 장소          |
| 판단  | 지도 기반 경로, 목표 속도 결정, 배달 가능 여부, 배달 소요 시간 |
| 제어  | 모터 제어, 카메라 작동, 정지, 출발, 종료, 상태 변환       |

## 4. Hard / Firm / Soft 분류표 — Hard 항목의 마감 초과 결과

|      |                          |
| ---- | ------------------------ |
| Hard | 보행자 인식, 장애물 감지, 모터 속도 제어 |
| Firm | 위치 파악, 지도 기반 경로 계획       |
| Soft | 배달 완료 사진 업로드, 운행 로그 집계   |

## 5. 주기, 지연, 지터 구분

|     |          |
| --- | -------- |
| 주기  | 76ms     |
| 지연  | 80ms     |
| 지터  | 72~102ms |

# 문제 2. 원격 접속(SSH)과 센서 장치 경로 고정

## 1. localhost

```bash
#who
pa2      tty2         2026-08-25 08:37 (tty2)
pa2      pts/10       2026-08-26 16:37 (127.0.0.1)

#echo $SSH_CONNECTION
127.0.0.1 43914 127.0.0.1 22
```

## 2.

공개키: 서버는 모두가 접속 할 수 있는 공개적인 공간 이기 때문에. 짝이 맞는 개인키만이 공개키를 맞춰 서버에 접속 할 수 있다.

## 3. 헤드리스 운용, scp

```bash
#헤드리스 운용
pa2@pa2-Legion-Pro-5-16IAX10:~$ ssh pa2@localhost df -h
파일 시스템     크기  사용  가용 사용% 마운트위치
tmpfs           3.1G  3.3M  3.1G    1% /run
/dev/nvme0n1p5  429G   39G  369G   10% /
tmpfs            16G  658M   15G    5% /dev/shm
tmpfs           5.0M  4.0K  5.0M    1% /run/lock
efivarfs        268K  232K   32K   89% /sys/firmware/efi/efivars
tmpfs            16G     0   16G    0% /run/qemu
/dev/nvme0n1p1  446M   53M  394M   12% /boot/efi
tmpfs           3.1G  1.7M  3.1G    1% /run/user/1000

#scp
pa2@pa2-Legion-Pro-5-16IAX10:~$ scp test/test.txt localhost:~/
pa2@localhost's password: 
test.txt                                      100%    0     0.0KB/s   00:00
```

## 4. 두 장치를 구분한 속성

| | lidar | Imu |
| --- | --- | --- |
| KERNEL | loop7 | loop24 |
| diskseq | 65 | 66 |
| stat | 126 0 3536 10 | 136 0 2688 0 |

## 5. 
| 속성|연산자 |설명 |
| --- | --- | --- |
| ATTR{loop/backing_file} | ==  조건부| 장치와 연결 되어 있는 파일을 선별 |
| SYMLINK | += 추가 | /dev/ 뒤에 문자열 추가| 


## 6. 재연결 후 확인
```
pa2@pa2-Legion-Pro-5-16IAX10:~/fake_sensors$ ls -l /dev/robot*
lrwxrwxrwx 1 root root 6 Aug 26 17:41 /dev/robot_imu -> loop22
lrwxrwxrwx 1 root root 5 Aug 26 17:39 /dev/robot_lidar -> loop7
```

## 7.

MODE

# 문제3.

## 1. 저장소, PR URL

저장소
- https://github.com/cowsjh/physicalai-lv1-assignments.git
PR URL
- https://github.com/cowsjh/physicalai-lv1-assignments/pull/1

## 2. 리뷰 코멘트와 반영 커밋

![pr](PR.png)
![prcomments](PR-comments.png)

## 3. 충돌이 난 파일과 줄.

README.md, 10번째 줄

```bash
pa2@pa2-Legion-Pro-5-16IAX10:~/git/physicalai-lv1-assignments$ git merge branch-b
자동 병합: README.md
충돌 (내용): README.md에 병합 충돌
자동 병합이 실패했습니다. 충돌을 바로잡고 결과물을 커밋하십시오.
```
기존에 있던(먼저 PR된) 커밋과 이후의 커밋 둘중 하나를 선택.

## 4. merge/ rebase

merge 는 브런치 에서 main으로 붙는 모양이지만, rebase 는 이전의 커밋 들이 main 의 업스트림 위로 올라 오면서 같은 선상에있는것 처럼 보인다.
![alt text](image-2.png)

## 5.

일반 적인 경우 merge를 쓰지만, 히스토리를 정리 하고 싶거나 다른 브런치의 수정 사항을 비교하며 테스트 해야할때 rebase로 새로 가져오면 충둘을 방지 할 수 있다.

