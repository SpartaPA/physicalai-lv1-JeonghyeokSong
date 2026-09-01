#include<iostream>
#include<vector>
#include<memory>
#include<cmath>

class Sensor
{
public:
    virtual void read() = 0;
    // ~Sensor() { std::cout << "~Sensor\n"; }
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

double distance(const Point& a, const Point& b)
{
    return sqrt(pow((a.x-b.x),2) + pow((a.y-b.y),2));
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

    // std::cout << "블록 진입 전\n";
    // {
    //     Lidar stack_lidar(1,1);
    //     auto heap_imu = std::make_unique<Imu>();
    // }
    // std::cout << "블록 빠져나옴\n";

    Point a {1.0,1.5};
    Point b {2.0,1.0};

    double dist {distance(a,b)};
    std::cout << dist << '\n';
    return 0;
}