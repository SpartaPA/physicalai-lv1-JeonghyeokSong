import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import (DurabilityPolicy, HistoryPolicy, QoSProfile,
                       ReliabilityPolicy)
from turtle_interfaces.action import DrawPolygon
from turtlesim.msg import Pose

def normalize_angle(a: float) -> float:
    return math.atan2(math.sin(a), math.cos(a))

class _Interrupted(Exception):

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason

class PolygonActionServer(Node):

    def __init__(self):
        super().__init__('polygon_action_server')

        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        self.declare_parameter('control_rate', 20.0)
        self.declare_parameter('segment_timeout_factor', 3.0)

        self._cb_group = ReentrantCallbackGroup()
        self._latest_pose = None
        self._busy = False

        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10,
                         reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.VOLATILE)
        self._pose_sub = self.create_subscription(
            Pose, 'turtle1/pose', self._on_pose, qos, callback_group=self._cb_group)
        self._cmd_pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)

        self._server = ActionServer(
            self, DrawPolygon, 'draw_polygon',
            execute_callback=self._execute,
            goal_callback=self._on_goal,
            cancel_callback=self._on_cancel,
            callback_group=self._cb_group,
        )
        self.get_logger().info('polygon_action_server 시작: 액션 /draw_polygon 대기 중')

    def _on_pose(self, msg: Pose):
        self._latest_pose = msg

    def _on_goal(self, goal_request: DrawPolygon.Goal):
        if goal_request.sides < 3:
            self.get_logger().warn(f'goal 거절: sides={goal_request.sides} (3 이상이어야 함)')
            return GoalResponse.REJECT
        if goal_request.side_length <= 0.0:
            self.get_logger().warn(f'goal 거절: side_length={goal_request.side_length} (양수여야 함)')
            return GoalResponse.REJECT
        if self._busy:
            self.get_logger().warn('goal 거절: 이미 다른 다각형을 그리는 중')
            return GoalResponse.REJECT
        self.get_logger().info(f'goal 수락: sides={goal_request.sides}, side_length={goal_request.side_length}')
        return GoalResponse.ACCEPT

    def _on_cancel(self, goal_handle):
        self.get_logger().warn('취소 요청 수신 — 실행 루프에서 즉시 정지합니다')
        return CancelResponse.ACCEPT

    def _stop(self):
        self._cmd_pub.publish(Twist())

    def _check_interrupt(self, goal_handle):
        if not rclpy.ok():
            raise _Interrupted('shutdown')
        if goal_handle.is_cancel_requested:
            raise _Interrupted('cancel')

    def _drive_straight(self, goal_handle, length, v_max, period, timeout_factor):
        start = self._latest_pose
        deadline = time.monotonic() + (length / v_max) * timeout_factor + 1.0
        twist = Twist()
        traveled = 0.0
        while True:
            self._check_interrupt(goal_handle)
            cur = self._latest_pose
            traveled = math.hypot(cur.x - start.x, cur.y - start.y)
            remaining = length - traveled
            if remaining <= 0.0:
                break
            if time.monotonic() > deadline:
                raise _Interrupted('timeout')
            twist.linear.x = min(v_max, max(0.2, 2.0 * remaining))
            self._cmd_pub.publish(twist)
            time.sleep(period)
        self._stop()
        return traveled

    def _turn(self, goal_handle, angle, w_max, period, timeout_factor):
        prev = self._latest_pose.theta
        turned = 0.0
        deadline = time.monotonic() + (angle / w_max) * timeout_factor + 1.0
        twist = Twist()
        while True:
            self._check_interrupt(goal_handle)
            cur = self._latest_pose.theta
            turned += normalize_angle(cur - prev)
            prev = cur
            remaining = angle - turned
            if remaining <= 0.0:
                break
            if time.monotonic() > deadline:
                raise _Interrupted('timeout')
            twist.angular.z = min(w_max, max(0.2, 2.0 * remaining))
            self._cmd_pub.publish(twist)
            time.sleep(period)
        self._stop()

    def _execute(self, goal_handle):
        goal = goal_handle.request
        sides, length = goal.sides, goal.side_length
        v_max = self.get_parameter('linear_speed').value
        w_max = self.get_parameter('angular_speed').value
        period = 1.0 / self.get_parameter('control_rate').value
        timeout_factor = self.get_parameter('segment_timeout_factor').value
        exterior_angle = 2.0 * math.pi / sides

        feedback = DrawPolygon.Feedback()
        result = DrawPolygon.Result()
        total = 0.0
        self._busy = True
        try:
            t0 = time.monotonic()
            while self._latest_pose is None:
                self._check_interrupt(goal_handle)
                if time.monotonic() - t0 > 3.0:
                    self.get_logger().error('/turtle1/pose 가 오지 않아 abort')
                    goal_handle.abort()
                    result.total_distance = 0.0
                    return result
                time.sleep(period)

            for i in range(sides):
                total += self._drive_straight(goal_handle, length, v_max, period, timeout_factor)
                self._turn(goal_handle, exterior_angle, w_max, period, timeout_factor)
                feedback.completed_sides = i + 1
                feedback.progress = float(i + 1) / float(sides)
                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f'변 {i + 1}/{sides} 완료 (누적 {total:.2f} m)')

            goal_handle.succeed()
            result.total_distance = total
            self.get_logger().info(f'다각형 완성: 총 이동 거리 {total:.2f} m')
            return result

        except _Interrupted as e:
            if rclpy.ok():
                self._stop()
            result.total_distance = total
            if e.reason == 'cancel':
                goal_handle.canceled()
                self.get_logger().warn(f'취소됨 — 정지. 그때까지 이동 거리 {total:.2f} m')
            elif e.reason == 'timeout':
                goal_handle.abort()
                self.get_logger().error('구간 타임아웃(벽에 막혔나요?) — abort')
            else:
                try:
                    goal_handle.abort()
                except Exception:
                    pass
            return result
        finally:
            self._busy = False

def main(args=None):
    rclpy.init(args=args)
    node = PolygonActionServer()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('Ctrl+C — 정상 종료합니다')
    finally:
        executor.shutdown(timeout_sec=1.0)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
