#include <stdio.h>


// Driver program to test above functions
int main()
{
    int arr[7] = {64, 34, 25, 12, 22, 11, 90};

    int i, j, temp;
    int n = 7;
   for (i = 0; i < n-1; i=i+1)
   {
      // Last i elements are already in place
     for (j = 0; j < n-i-1; j= j+1)
     {
         if (arr[j] > arr[j+1])
         {
            temp = arr[j+1];
            arr[j+1] = arr[j];
            arr[j] = temp;
         }
    }
  }
  int out ;
  cout << "Sorted Array: " ;
  for (i=0; i < n-1; i = i+1)  {
    out = arr[i];
    //printf("%d ", arr[i]);
    cout << " " << out;
  }
}
