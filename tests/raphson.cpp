// C++ program for implementation of Newton Raphson Method for
// solving equations
#include <stdio.h>
float EPSILON  = 0.001;

// An example function whose solution is determined using
// Bisection Method. The function is x^3 - x^2  + 2
float func(float x)
{
    return x*x*x - x*x + 2.0;
}

// Derivative of the above function which is 3*x^x - 2*x
float derivFunc(float x)
{
    float d = 3.0*x*x - 2.0*x;
    return d;
}

void newtonRaphson(float x)
{

    float h = func(x) / derivFunc(x);
    //cout << "h1: " << h;
    printf("The  h is : %f ",h);

    if (h < 0.0){
      h = h*(-1.0);
    }
    while (h >= EPSILON )
    {
        h = func(x)/derivFunc(x);
        //cout << "h2: " << h;
        printf("The h2 : %f ",h);

        x = x - h;
    }

    printf("The value of the root is : %f ",x);
    //cout << "The value of the root is : " << x;
}

int main()
{
    float x0 = -20.0; // Initial values assumed
    newtonRaphson(x0);
    return 0;
}
