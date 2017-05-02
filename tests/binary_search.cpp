 #include <stdio.h>
 int main()
{
   int arr[5] = {2, 3, 4, 10, 40};
   int n = 5;
   int x = 40;
   int result = -1;
   result = -result;
   int l = 0;
   int r = 4;
   int m;
   while (l <= r)
  {
     m = l + (r-l)/2;

    // Check if x is present at mid
    if (arr[m] == x)
    {
        result =  m;
        break;
    }

    // If x greater, ignore left half
    if (arr[m] < x)
        l = m + 1;

    // If x is smaller, ignore right half
    else
         r = m - 1;
  }
  cout << "Index is " << result;


   return 0;
}
