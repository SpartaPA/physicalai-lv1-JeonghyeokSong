import rclpy, math
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

class TurtleTF(Node):
    def __init__(self):
        super().__init__('turtle_tf_broadcaster')
        self.br = TransformBroadcaster(self)
        self.create_subscription(Pose, 'turtle1/pose', self.on_pose, 10)

    def on_pose(self, msg):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'turtle1'

        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0

        qz = math.sin(msg.theta / 2.0)
        qw = math.cos(msg.theta / 2.0)

        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.br.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleTF()
    rclpy.spin(node)
    rclpy.shutdown()