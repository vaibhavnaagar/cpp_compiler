/*
                OVERLOADING OPERATOR

*/


#include <iostream>
using namespace std;

class Box {
   public:
	
      double getVolume(void) {
         return length * breadth * height;
      }

      void setLength( double len ) {
         length = len;
      }

      // Overload + operator to add two Box objects.
      Box operator+(const Box& b) {
         Box box;
         box.length = this->length + b.length;
         return box;
      }

   private:
      double length;      // Length of a box
  };

// Main function for the program
int main( ) {
   Box Box1;                // Declare Box1 of type Box
   double volume = 0.0;     // Store the volume of a box here

   // box 1 specification
   Box1.setLength(6.0);
    

   // volume of box 1
   volume = Box1.getVolume();
   cout << "Volume of Box1 : " << volume <<endl;


   return 0;
}
