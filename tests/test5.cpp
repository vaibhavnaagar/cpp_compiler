/*
            Namespaces
*/


#include <iostream>
//using namespace std;

// first name space
namespace first_space{
  int mn;
   void func(){
    //  cout << "Inside first_space" << endl;
   }

   // second name space
   namespace second_space{
      void func3(){
        // cout << "Inside second_space" << endl;
      }
   }
}

namespace second_space{
   void func2(){
     // cout << "Inside second_space" << endl;
   }
}

namespace x {
  int b;
}
//using namespace first_space;
int main () {
  using second_space::func2;

   // This calls function from second name space.
   func2();

   return 0;
}
