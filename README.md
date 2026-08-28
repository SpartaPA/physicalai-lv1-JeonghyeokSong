| 부품       | 주기         | 지연 예산   | 초당 데이터 크기         | 데이터 타입                    | 비고                                 |
| -------- | ---------- | ------- | ----------------- | ------------------------- | ---------------------------------- |
| 2D Lidar | 8hz        | 125ms   | 0.257mbps         | sensor_msgs/LaserScan     | float32 / 초당 8000 샘플               |
| 카메라      | 1080p30fps | 33.33ms | 622mbps, 1492mbps | sensor_msgs/Image.msg     | flfoat32 / raw(10bit), RGB         |
| IMU      | 100hz      | 10ms    | 0.2368mbps        | sensor_msgs/Imu.msg       | float 64 / 각속도, 선속도, 쿼터니언 (공분산 포함) |
| encoder  | 1khz       | 1ms     | 0.768mbps         | sensor_msg/JointState.msg | 4륜                                 |
| LTE      |            | 30ms    |                   |                           | 하향 150mbps/ 상향 50mbps              |


test branch-b