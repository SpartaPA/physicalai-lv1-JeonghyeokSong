import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (DurabilityPolicy, HistoryPolicy, QoSProfile,
                       ReliabilityPolicy)
from turtle_interfaces.msg import Waypoint, WaypointList

class WaypointPublisher(Node):

    def __init__(self):
        super().__init__('waypoint_publisher')

        self.declare_parameter('durability', 'transient_local')
        self.declare_parameter('frame_id', 'world')
        durability_str = self.get_parameter('durability').value
        if durability_str == 'transient_local':
            durability = DurabilityPolicy.TRANSIENT_LOCAL
        elif durability_str == 'volatile':
            durability = DurabilityPolicy.VOLATILE
        else:
            raise ValueError(f'durability 파라미터는 transient_local 또는 volatile 이어야 합니다: {durability_str}')

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=durability,
        )
        self._pub = self.create_publisher(WaypointList, 'waypoints', qos)

        self._timer = self.create_timer(1.0, self._publish_once)
        self.get_logger().info(f'waypoint_publisher 시작: durability={durability_str}, '
                               'reliability=reliable, depth=1 — 1초 뒤 1회 발행')

    def _make_waypoint(self, x, y, tolerance, label) -> Waypoint:
        wp = Waypoint()
        wp.x = float(x)
        wp.y = float(y)
        wp.tolerance = float(tolerance)
        wp.label = label
        return wp

    def _publish_once(self):
        self._timer.cancel()

        msg = WaypointList()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value

        msg.waypoints.append(self._make_waypoint(2.0, 2.0, 0.3, 'corner_A'))
        msg.waypoints.append(self._make_waypoint(9.0, 2.0, 0.3, 'corner_B'))
        msg.waypoints.append(self._make_waypoint(9.0, 9.0, 0.3, 'corner_C'))
        msg.waypoints.append(self._make_waypoint(2.0, 9.0, 0.3, 'corner_D'))

        self._pub.publish(msg)
        labels = [wp.label for wp in msg.waypoints]
        self.get_logger().info(f'/waypoints 발행: {len(msg.waypoints)}개 {labels} '
                               f'(frame_id={msg.header.frame_id}). '
                               '`ros2 topic echo /waypoints` 로 중첩 필드를 확인하세요')

def main(args=None):
    rclpy.init(args=args)
    node = WaypointPublisher()
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
