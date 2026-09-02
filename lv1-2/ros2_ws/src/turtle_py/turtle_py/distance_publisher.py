import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Float32
import math

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('distance_publisher')
        self.declare_parameter('publish_rate', 10.0)

        self.last_pose = None

        self.subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.publisher = self.create_publisher(Float32, "/turtle_distance",10)
        self.create_timer(1.0/self.get_parameter('publish_rate').value, self.timer_callback)

    def pose_callback(self,msg):
        self.last_pose = msg.x, msg.y

    def calc_distance(self,msg):
        return math.hypot(msg[0], msg[1])

    def timer_callback(self):
        if self.last_pose == None:
            return

        msg = Float32()
        msg.data = self.calc_distance(self.last_pose)

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DistancePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
    