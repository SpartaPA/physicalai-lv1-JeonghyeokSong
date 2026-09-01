#include"motor.hpp"
#include<iostream>

int main()
{
    Motor motor{2048};

    std::cout << motor.get_res() << std::endl;

    return 0;
}