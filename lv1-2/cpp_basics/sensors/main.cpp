#include<iostream>

class Sensor
{
public:
    virtual void read() = 0;
};

class Lidar : public Sensor
{
public:
    Lidar(double limit_angle, unsigned int point_counts )
    : limit_angle{limit_angle}, point_counts{point_counts} {}
    void read(){ std::cout << "Lidar data" << std::endl;}

private:
    double limit_angle;
    unsigned int point_counts;
};

class Imu : public Sensor
{
public:
    void read(){std::cout << "Imu data" << std::endl;}
};


int main()
{
    Sensor* p = new Lidar(10.0,8000);
    p->read();

    delete p;
    

    return 0;
}