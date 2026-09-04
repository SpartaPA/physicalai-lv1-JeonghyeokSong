#include <chrono>
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

class cpp_subscriber : public rclcpp::Node
{
public:
    cpp_subscriber() : Node("cpp_subscriber")
    {
        subscription_ = this->create_subscription<std_msgs::msg::Float32>(
            "/turtle_distance", 10, std::bind(&cpp_subscriber::topic_callback, this, std::placeholders::_1));
   
    }

    void topic_callback(const std_msgs::msg::Float32::SharedPtr msg) const
    {
        RCLCPP_INFO(this->get_logger(), "[cpp subscriber] distance: '%f'", msg->data);
    }
   
private:
    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_;
    
};


int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<cpp_subscriber>());
    rclcpp::shutdown();
    return 0;
}