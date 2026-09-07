import  rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from turtle_interfaces.msg import WaypointList
from visualization_msgs.msg import Marker, MarkerArray

class WaypointMarkers(Node):
    def __init__(self):
        super().__init__('waypoint_markers')
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST, depth = 1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.create_subscription(WaypointList, '/waypoints', self.on_wps, qos)
        self.pub = self.create_publisher(MarkerArray, '/waypoint_markers', 10)

    def on_wps(self, msg):
        arr = MarkerArray()
        for i, wp in enumerate(msg.waypoints):

            m = Marker()
            m.header.frame_id = 'world'
            m.header.stamp = self.get_clock().now().to_msg()
            m.ns = 'waypoints'
            m.id = i
            m.type = Marker.SPHERE
            m.action = Marker.ADD
            m.pose.position.x = wp.x
            m.pose.position.y = wp.y
            m.pose.position.z = 0.0
            m.pose.orientation.w = 1.0
            m.scale.x = 0.2
            m.scale.y = 0.2
            m.scale.z = 0.2
            m.color.r = 1.0
            m.color.g = 0.0
            m.color.b = 0.0
            m.color.a = 1.0

            arr.markers.append(m)
        self.pub.publish(arr)

def main(args=None):
    rclpy.init(args=args)
    node = WaypointMarkers()
    rclpy.spin(node)
    rclpy.shutdown()