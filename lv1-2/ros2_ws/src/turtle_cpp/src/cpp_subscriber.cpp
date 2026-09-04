#include <chrono>
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

class cpp_subscriber : public rclcpp::Node
{
public:
    cpp_subscriber(/* args */);
    ~cpp_subscriber();
private:
    rclcpp::Publisher<std_msgs::msg::float32>::SharedPtr publisher_;
};


