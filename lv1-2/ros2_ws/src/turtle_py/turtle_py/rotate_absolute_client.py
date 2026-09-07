import argparse
import math
import sys

import rclpy
from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (DurabilityPolicy, HistoryPolicy, QoSProfile,
                       ReliabilityPolicy)
from rclpy.utilities import remove_ros_args
from turtlesim.action import RotateAbsolute
from turtlesim.msg import Pose

STATUS_NAME = {
    GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED',
    GoalStatus.STATUS_CANCELED: 'CANCELED',
    GoalStatus.STATUS_ABORTED: 'ABORTED',
}

class RotateAbsoluteClient(Node):

    def __init__(self, target_theta: float, cancel_after):
        super().__init__('rotate_absolute_client')
        self._target = target_theta
        self._cancel_after = cancel_after

        self._client = ActionClient(self, RotateAbsolute, 'turtle1/rotate_absolute')

        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10,
                         reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.VOLATILE)
        self._pose_sub = self.create_subscription(Pose, 'turtle1/pose', self._on_pose, qos)
        self._latest_theta = None

        self._goal_handle = None
        self._cancel_timer = None
        self.done = False

    def _on_pose(self, msg: Pose):
        self._latest_theta = msg.theta

    def send_goal(self):
        if not self._client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('액션 서버 /turtle1/rotate_absolute 가 없습니다 (turtlesim 실행 중?)')
            self.done = True
            return
        goal = RotateAbsolute.Goal()
        goal.theta = float(self._target)
        self.get_logger().info(f'goal 전송: theta = {goal.theta:.3f} rad '
                               f'(현재 theta = {self._latest_theta})')
        send_future = self._client.send_goal_async(goal, feedback_callback=self._on_feedback)
        send_future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('goal 이 거절되었습니다')
            self.done = True
            return
        self.get_logger().info('goal 수락됨 — 피드백 대기')
        self._goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_result)

        if self._cancel_after is not None:
            self._cancel_timer = self.create_timer(self._cancel_after, self._on_cancel_timer)

    def _on_feedback(self, feedback_msg):
        remaining = feedback_msg.feedback.remaining
        self.get_logger().info(f'피드백: remaining = {remaining:+.3f} rad',
                               throttle_duration_sec=0.25)

    def _on_cancel_timer(self):
        self._cancel_timer.cancel()
        theta_at_cancel = self._latest_theta
        self.get_logger().warn(f'취소 요청 전송 (요청 시점 theta = {theta_at_cancel:.3f} rad)')
        cancel_future = self._goal_handle.cancel_goal_async()
        cancel_future.add_done_callback(
            lambda f: self._on_cancel_response(f, theta_at_cancel))

    def _on_cancel_response(self, future, theta_at_cancel):
        resp = future.result()
        if resp.return_code == CancelGoal.Response.ERROR_NONE and len(resp.goals_canceling) > 0:
            self.get_logger().warn(f'취소 수락됨 (서버가 중단 처리 중). 취소 시점 theta = {theta_at_cancel:.3f} rad')
        else:
            self.get_logger().error(f'취소 거절: return_code={resp.return_code} '
                                    '(이미 끝난 goal 이면 ERROR_GOAL_TERMINATED=3)')

    def _on_result(self, future):
        wrapped = future.result()
        status = wrapped.status
        result = wrapped.result
        name = STATUS_NAME.get(status, str(status))
        self.get_logger().info(f'결과 수신: status={name}, delta={result.delta:+.3f} rad, '
                               f'현재 theta = {self._latest_theta}')
        self.done = True

def main(args=None):
    rclpy.init(args=args)
    parser = argparse.ArgumentParser(description='turtlesim RotateAbsolute action client')
    parser.add_argument('--theta', type=float, default=math.pi / 2,
                        help='목표 절대 각도 [rad] (기본 pi/2)')
    parser.add_argument('--cancel-after', type=float, default=None,
                        help='이 시간[초] 뒤 취소 요청을 보냄 (생략하면 취소 안 함)')
    cli = parser.parse_args(remove_ros_args(sys.argv)[1:])

    node = RotateAbsoluteClient(cli.theta, cli.cancel_after)
    try:
        node.send_goal()
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('Ctrl+C — 중단합니다')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
