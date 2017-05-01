// C program for implementation of Bubble sort
#include <stdio.h>


// Driver program to test above functions
int main()
{
    int arr[7] = {64, 34, 25, 12, 22, 11, 90};

    int i, j;
    int n = 7;
   for (i = 0; i < n-1; i++)      
 
       // Last i elements are already in place   
       for (j = 0; j < n-i-1; j++) {
           if (arr[j] > arr[j+1]){
            int temp = arr[j+1];
  arr[j+1] = arr[j];
    arr[j] = temp;
  }
}
    for (i=0; i < 7; i++)  {
      out = arr[i];
      cout << " " << out;
    }

}