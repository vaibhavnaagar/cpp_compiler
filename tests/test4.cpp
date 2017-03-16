/*
              Class and their methods and switch-case
*/

#include<iostream.h>
#include<stdlib.h>
#include<conio.h>
#define pi 3.14
class fn
{
      public:
        void area(int);  //circle
        void area(int,int);  //rectangle
        void area(float ,int,int);  //triangle
};

void fn::area(int a)
{
      cout<<"Area of Circle:"<<pi*a*a;
}
void fn::area(int a,int b)
{
      cout<<"Area of rectangle:"<<a*b;
}
void fn::area(float t,int a,int b)
{
      cout<<"Area of triangle:"<<t*a*b;
}

void main()
{
     int ch;
     int a,b,r;
     clrscr();
     fn obj;
     cout<<"\n\t\tFunction Overloading";
     cout<<"\n1.Area of Circle\n2.Area of Rectangle\n3.Area of Triangle\n4.Exit\n:";
     cout<<"Enter your Choice:";
     cin>>ch;

     switch(ch)
     {
              case 1:
                cout<<"Enter Radious of the Circle:";
                cin>>r;
                obj.area(r);
                break;
              case 2:
                cout<<"Enter Sides of the Rectangle:";
                cin>>a>>b;
                obj.area(a,b);
                break;
              case 3:
                cout<<"Enter Sides of the Triangle:";
                cin>>a>>b;
                obj.area(0.5,a,b);
                break;
              case 4:
                exit(0);
     }
getch();
}
