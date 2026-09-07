import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Float32
import math
from rcl_interfaces.msg import SetParametersResult

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('distance_publisher')
        self.declare_parameter('publish_rate', 10.0)
        
        self.last_pose = None

        self.subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.publisher = self.create_publisher(Float32, "/turtle_distance",10)
        rate = self.get_parameter('publish_rate').value
        if rate <= 0:
            self.get_logger().warn("publish_rate must be > 0, setting to default 10.0")
            rate = 10.0
        self.timer = self.create_timer(1.0/rate, self.timer_callback)
        self.add_on_set_parameters_callback(self.on_params)

    def on_params(self,params):
        for p in params:
            if p.name == "publish_rate":
                rate = p.value
                if rate <= 0:
                    return SetParametersResult(successful=False, reason="publish_rate must be > 0")
                self.destroy_timer(self.timer)
                self.timer = self.create_timer(1.0/rate, self.timer_callback)
        return SetParametersResult(successful=True)

    def pose_callback(self,msg):
        self.last_pose = msg.x, msg.y

    def calc_distance(self,msg):
        return math.hypot(msg[0], msg[1])

    def timer_callback(self):
        if self.last_pose is None:
            return

        msg = Float32()
        msg.data = self.calc_distance(self.last_pose)
        self.get_logger().info(f"[py publisher] distance: {msg.data:.2f}")
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
