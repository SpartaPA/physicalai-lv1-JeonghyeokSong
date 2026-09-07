import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (DurabilityPolicy, HistoryPolicy, QoSProfile,
                       ReliabilityPolicy)
from std_msgs.msg import Float32

try:
    from rclpy.qos_event import SubscriptionEventCallbacks
except ImportError:
    SubscriptionEventCallbacks = None

class QosSubscriber(Node):

    def __init__(self):
        super().__init__('qos_subscriber')

        self.declare_parameter('topic', 'turtle_distance')
        self.declare_parameter('msg_type', 'Float32')
        self.declare_parameter('reliability', 'reliable')
        self.declare_parameter('durability', 'volatile')
        self.declare_parameter('history_depth', 10)
        self.declare_parameter('callback_delay', 0.0)

        topic = self.get_parameter('topic').value
        msg_type = self.get_parameter('msg_type').value
        reliability_str = self.get_parameter('reliability').value
        durability_str = self.get_parameter('durability').value
        depth = self.get_parameter('history_depth').value
        self._delay = self.get_parameter('callback_delay').value

        reliability = {
            'reliable': ReliabilityPolicy.RELIABLE,
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
        }.get(reliability_str)
        durability = {
            'volatile': DurabilityPolicy.VOLATILE,
            'transient_local': DurabilityPolicy.TRANSIENT_LOCAL,
        }.get(durability_str)
        if reliability is None or durability is None or depth < 1:
            raise ValueError('reliability=reliable|best_effort, durability=volatile|transient_local, '
                             f'history_depth>=1 이어야 합니다 (받은 값: {reliability_str}, {durability_str}, {depth})')

        if msg_type == 'Float32':
            msg_cls = Float32
        elif msg_type == 'WaypointList':
            from turtle_interfaces.msg import WaypointList
            msg_cls = WaypointList
        else:
            raise ValueError(f'msg_type 은 Float32 또는 WaypointList: {msg_type}')

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=depth,
            reliability=reliability,
            durability=durability,
        )

        self._sub = None
        if SubscriptionEventCallbacks is not None:
            try:
                events = SubscriptionEventCallbacks(incompatible_qos=self._on_incompatible_qos)
                self._sub = self.create_subscription(msg_cls, topic, self._on_msg, qos,
                                                     event_callbacks=events)
            except Exception as e:
                self.get_logger().warn(f'incompatible_qos 이벤트 미지원 ({e}) — 이벤트 없이 구독합니다')
        if self._sub is None:
            self._sub = self.create_subscription(msg_cls, topic, self._on_msg, qos)

        self._count_total = 0
        self._count_window = 0
        self._stats_timer = self.create_timer(2.0, self._on_stats)

        self.get_logger().info(
            f'qos_subscriber 시작: topic={topic} type={msg_type} '
            f'reliability={reliability_str} durability={durability_str} depth={depth} '
            f'callback_delay={self._delay}s')

    def _on_msg(self, msg):
        self._count_total += 1
        self._count_window += 1
        if hasattr(msg, 'waypoints'):
            labels = [wp.label for wp in msg.waypoints]
            self.get_logger().info(f'#{self._count_total} WaypointList: {len(msg.waypoints)}개 {labels} '
                                   f'frame_id={msg.header.frame_id}')
        else:
            self.get_logger().info(f'#{self._count_total} 수신: {msg.data:.3f}')

        if self._delay > 0.0:
            time.sleep(self._delay)

    def _on_stats(self):
        self.get_logger().info(f'[통계] 지난 2초 처리 {self._count_window}개 (누적 {self._count_total}개)'
                               + ('' if self._count_window else ' — 0개라면 QoS 비호환이나 발행자 부재를 의심'))
        self._count_window = 0

    def _on_incompatible_qos(self, event):
        self.get_logger().error(
            f'QoS 비호환 이벤트! total_count={event.total_count}, last_policy_kind={event.last_policy_kind} '
            '→ `ros2 topic info -v` 로 발행자/구독자 QoS 를 비교하세요')

def main(args=None):
    rclpy.init(args=args)
    node = QosSubscriber()
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
