import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
import math

class DriverSquare(Node):
    def __init__(self):
        super().__init__("driver_square")

        self.subscriber = self.create_subscription(Pose, '/turtle1/pose' , self.pose_callback,10)
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.tick  = 0
        self.pose = None
        self.phase ="forward"
        self.x0 = None; self.y0 = None
        # self.side = 0

    def pose_callback(self, msg):
        self.pose = msg

    def timer_callback(self):
        if self.pose == None :
            return
        d = 0.0
        if self.phase == "forward":

            if self.x0 is None :
                self.x0, self.y0 = self.pose.x, self.pose.y

            d = math.hypot(self.pose.x - self.x0, self.pose.y - self.y0)
            msg = Twist()
            msg.linear.x = 1.0
            self.publisher.publish(msg)
            if d >= 2.0 :
                self.phase = "turn"
                self.tick = 0

        elif self.phase == "turn":
            self.tick += 1
            msg = Twist()
            msg.angular.z = math.pi*0.5
            self.publisher.publish(msg)
            if self.tick >= 10:
                self.phase = "forward"
                self.x0 = None

        self.get_logger().info(
    f"[{self.phase}] tick={self.tick} d={d:.2f} x0={self.x0} pos=({self.pose.x:.2f},{self.pose.y:.2f})")
        
def main(args=None):
    rclpy.init(args=args)
    node = DriverSquare()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

