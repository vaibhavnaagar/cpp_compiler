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
      void func2(){
        // cout << "Inside second_space" << endl;
      }
   }
}

namespace first_space {
  int abc;
}

//using namespace first_space::second_space;
int main () {

   // This calls function from second name space.
   //func();

   return 0;
}
