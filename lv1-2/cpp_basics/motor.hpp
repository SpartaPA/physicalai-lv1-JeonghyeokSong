#ifndef __MOTOR_HPP__
#define __MOTOR_HPP__

class Motor
{
public:
    Motor( unsigned int resolution);
    int get_res() { return this->resolution; }
private :
    unsigned int resolution;
    unsigned int id;
};

#endif
