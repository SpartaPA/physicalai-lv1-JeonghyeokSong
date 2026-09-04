#include <memory>
#include <chrono>
#include <cmath>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"

class DistancePublisher : public rclcpp::Node
{
public:
    DistancePublisher() : Node("distance_publisher")
    {
        publisher_ = this->create_publisher<std_msgs::msg::Float32>("/turtle_distance", 10);
        subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose", 10, std::bind(&DistancePublisher::pose_callback, this, std::placeholders::_1));
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&DistancePublisher::publish_distance, this));
    }
    double calculate_distance()
    {
        return std::hypot(last_x, last_y);
    }
    void publish_distance()
    {
        if (!have_new_pose_) return;
        
        auto message = std_msgs::msg::Float32();
        message.data = calculate_distance();
        RCLCPP_INFO(this->get_logger(), "distance: '%f'", message.data);
        publisher_->publish(message);
    }
    void pose_callback(const turtlesim::msg::Pose::SharedPtr msg)
    {
        // Update last known position
        last_x = msg->x;
        last_y = msg->y;
        have_new_pose_ = true;
    }

private:
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_;
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
    bool have_new_pose_ = false;
    double last_x = 0.0, last_y = 0.0;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DistancePublisher>());
    rclcpp::shutdown();
    return 0;
}