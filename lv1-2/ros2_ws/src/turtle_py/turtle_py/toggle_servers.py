import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (DurabilityPolicy, HistoryPolicy, QoSProfile,
                       ReliabilityPolicy)
from std_srvs.srv import SetBool, Trigger
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute

class ToggleServers(Node):

    def __init__(self):
        super().__init__('turtle_toggle_servers')

        self.declare_parameter('start_enabled', False)
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 0.8)
        self._enabled = self.get_parameter('start_enabled').value

        self._latest_pose = None
        self._home = None

        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10,
                         reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.VOLATILE)
        self._pose_sub = self.create_subscription(Pose, 'turtle1/pose', self._on_pose, qos)
        self._cmd_pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)

        self._timer = self.create_timer(0.1, self._on_timer)

        self._enable_srv = self.create_service(SetBool, 'enable_driving', self._on_enable_driving)
        self._save_srv = self.create_service(Trigger, 'save_home', self._on_save_home)
        self._go_home_srv = self.create_service(Trigger, 'go_home', self._on_go_home)

        self._teleport_cli = self.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')

        self.get_logger().info(f'toggle_servers 시작 (주행 {"ON" if self._enabled else "OFF"}). '
                               '서비스: /enable_driving /save_home /go_home')

    def _on_pose(self, msg: Pose):
        self._latest_pose = msg

    def _on_timer(self):
        if not self._enabled:
            return
        twist = Twist()
        twist.linear.x = self.get_parameter('linear_speed').value
        twist.angular.z = self.get_parameter('angular_speed').value
        self._cmd_pub.publish(twist)

    def _on_enable_driving(self, request: SetBool.Request, response: SetBool.Response):
        self._enabled = request.data
        if not self._enabled:
            self._cmd_pub.publish(Twist())
        response.success = True
        response.message = f'driving {"enabled" if self._enabled else "disabled"}'
        self.get_logger().info(f'/enable_driving ← data={request.data} → {response.message}')
        return response

    def _on_save_home(self, request: Trigger.Request, response: Trigger.Response):
        if self._latest_pose is None:
            response.success = False
            response.message = '아직 /turtle1/pose 를 받지 못해 홈을 저장할 수 없습니다'
        else:
            p = self._latest_pose
            self._home = (p.x, p.y, p.theta)
            response.success = True
            response.message = f'home saved: x={p.x:.2f} y={p.y:.2f} theta={p.theta:.2f}'
        self.get_logger().info(f'/save_home → {response.message}')
        return response

    def _on_go_home(self, request: Trigger.Request, response: Trigger.Response):
        if self._home is None:
            response.success = False
            response.message = '저장된 홈이 없습니다. 먼저 /save_home 을 호출하세요'
            return response
        if not self._teleport_cli.service_is_ready():
            response.success = False
            response.message = '/turtle1/teleport_absolute 서버가 없습니다 (turtlesim 실행 중?)'
            return response

        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = self._home
        future = self._teleport_cli.call_async(req)
        future.add_done_callback(self._on_teleport_done)

        response.success = True
        response.message = f'teleport 요청 전송: ({req.x:.2f}, {req.y:.2f}, {req.theta:.2f}) — 결과는 로그 참조'
        self.get_logger().info(f'/go_home → {response.message}')
        return response

    def _on_teleport_done(self, future):
        if future.exception() is not None:
            self.get_logger().error(f'teleport 실패: {future.exception()}')
        else:
            self.get_logger().info('teleport 완료 — 홈으로 이동했습니다')

def main(args=None):
    rclpy.init(args=args)
    node = ToggleServers()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('Ctrl+C — 정상 종료합니다')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
