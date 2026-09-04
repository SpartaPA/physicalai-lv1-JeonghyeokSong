#include<iostream>
#include<vector>
#include<memory>
#include<cmath>
#include<algorithm>
#include<unordered_map>
#include<string>



class Sensor
{
public:
    virtual void read() = 0;
    virtual ~Sensor() { std::cout << "~Sensor\n"; }
};

class Lidar : public Sensor
{
public:
    Lidar(double limit_angle, unsigned int point_counts )
    : limit_angle{limit_angle}, point_counts{point_counts} {}
    void read(){ std::cout << "Lidar data would be here..." << std::endl;}
    ~Lidar() { std::cout << "~Lidar\n"; }

private:
    double limit_angle;
    unsigned int point_counts;
};

class Imu : public Sensor
{
public:
    void read(){std::cout << "Imu data would be here..." << std::endl;}
    ~Imu() { std::cout << "~Imu\n"; }
};

struct Point
{
    double x;
    double y;
};

double distance(const Point& a)
{
    return std::sqrt(a.x * a.x + a.y * a.y);
}

template<typename T>
T clamp(T value, T min, T max)
{
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

int main()
{
    
    std::vector<std::unique_ptr<Sensor>> sensors {};
    auto lidar = std::make_unique<Lidar>(30,8000);
    auto imu = std::make_unique<Imu>();

    sensors.push_back(std::move(lidar));
    sensors.push_back(std::move(imu));

    for (auto& s : sensors)
    {
        s->read();
    }

    std::cout << "블록 진입 전\n";
    {
        Lidar stack_lidar(1,1);
        auto heap_imu = std::make_unique<Imu>();
    }
    std::cout << "블록 빠져나옴\n";

    std::vector<Point> points {{1,2}, {.3,.2}, {5,6}};

    std::unordered_map<std::string, Point> point_map;
    Point last_lidar_point = {0.1, 0.2};
    point_map["lidar"] = last_lidar_point;
    points.push_back(last_lidar_point);

    Point last_imu_point = {0.3, 0.4};
    point_map["imu"] = last_imu_point;
    points.push_back(last_imu_point);
    
    int n = std::count_if(points.begin(), points.end(), [](const Point& p){ return distance(p) <= 3.5; });

    std::cout << "최근 lidar 측정값" << point_map["lidar"].x << ", " << point_map["lidar"].y << '\n';
    std::cout << "최근 imu 측정값" << point_map["imu"].x << ", " << point_map["imu"].y << '\n';

    std::cout << "0.5 이내 포인트 개수: " << n << '\n';

    double speed = clamp(7.4, 1.0, 5.0);
    int pixel = clamp(31, 100, 255);

    std::cout << "clamp speed: " << speed << '\n';
    std::cout << "clamp pixel: " << pixel << '\n';

    for (int i = 0; i < 10; ++i)
    {
        // Lidar* my_lidar = new Lidar(30, 8000);
        auto lidar = std::make_unique<Lidar>(30, 8000);
    }
    


    return 0;
}