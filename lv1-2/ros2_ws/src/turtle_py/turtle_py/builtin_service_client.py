import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import Empty
from turtlesim.srv import SetPen, Spawn, TeleportAbsolute

class BuiltinServiceClient(Node):

    def __init__(self):
        super().__init__('builtin_service_client')
        self.teleport_cli = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.set_pen_cli = self.create_client(SetPen, '/turtle1/set_pen')
        self.spawn_cli = self.create_client(Spawn, '/spawn')
        self.clear_cli = self.create_client(Empty, '/clear')

    def call(self, client, request, timeout_sec=5.0):
        name = client.srv_name
        if not client.wait_for_service(timeout_sec=timeout_sec):
            self.get_logger().error(f'{name}: 서버가 {timeout_sec}s 안에 뜨지 않았습니다 '
                                    '(turtlesim_node 가 실행 중인가요?)')
            return None
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout_sec)
        if not future.done():
            self.get_logger().error(f'{name}: {timeout_sec}s 안에 응답이 없습니다')
            return None
        if future.exception() is not None:
            self.get_logger().error(f'{name}: 예외 {future.exception()}')
            return None
        return future.result()

    def run_sequence(self):
        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = 5.5, 5.5, 0.0
        res = self.call(self.teleport_cli, req)
        self.get_logger().info(f'[1/4] teleport_absolute({req.x}, {req.y}, {req.theta}) '
                               f'→ {"OK" if res is not None else "FAIL"}')

        req = SetPen.Request()
        req.r, req.g, req.b, req.width, req.off = 255, 0, 0, 4, 0
        res = self.call(self.set_pen_cli, req)
        self.get_logger().info(f'[2/4] set_pen(r={req.r}, g={req.g}, b={req.b}, width={req.width}, off={req.off}) '
                               f'→ {"OK" if res is not None else "FAIL"}')

        req = Spawn.Request()
        req.x, req.y, req.theta, req.name = 2.0, 2.0, 0.0, 'turtle2'
        res = self.call(self.spawn_cli, req)
        if res is None:
            self.get_logger().info('[3/4] spawn → FAIL')
        elif res.name == '':
            self.get_logger().warn('[3/4] spawn → 빈 이름 반환 (이미 turtle2 가 있나요?)')
        else:
            self.get_logger().info(f'[3/4] spawn → 새 거북이 이름 "{res.name}" '
                                   f'(ros2 topic list 에서 /{res.name}/pose 확인)')

        res = self.call(self.clear_cli, Empty.Request())
        self.get_logger().info(f'[4/4] clear → {"OK" if res is not None else "FAIL"}')

def main(args=None):
    rclpy.init(args=args)
    node = BuiltinServiceClient()
    try:
        node.run_sequence()
    except (KeyboardInterrupt, ExternalShutdownException):
        node.get_logger().info('Ctrl+C — 중단합니다')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
