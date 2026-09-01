#include<iostream>

constexpr double g = 9.80665;

double s_dist ( double vel, double mu )
{
    return (vel*vel) / (mu*g);
}

int main()
{
    double vel{};
    double mu{};

    std::cout << "속도: ";
    std::cin >> vel;
    std::cout << "마찰: ";
    std::cin >> mu;
    std::cout << '\n';

    std::cout << s_dist(vel, mu) << std::endl;
}