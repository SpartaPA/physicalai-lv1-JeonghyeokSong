import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DistanceWatcher(Node):
    def __init__(self):
        super().__init__('distance_watcher')
        self.declare_parameter('warn_distance', 2.5)

        self.subscriber = self.create_subscription(Float32, '/turtle_distance', self.distance_callback, 10)

    def distance_callback(self, msg):
        threshold = self.get_parameter('warn_distance').value
        if msg.data > threshold:
            self.get_logger().warn(f"Distance {msg.data:.2f} > {threshold:.2f}!")
        else :
            pass

def main(args=None):
    rclpy.init(args=args)
    node = DistanceWatcher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()