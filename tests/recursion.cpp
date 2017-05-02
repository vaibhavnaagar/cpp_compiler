
int test(int n)
 {
   if (n == 0){
     return 1;
   }
 	int a = 1+ test(n-1);

 	return a;
 }

int main()
{
 // int c[3] = {3,4,5};
  //int i = 2;
  //int [1] = {1};
  int sum = 9;
  int n =5;
  sum = test(n);
 cout << "sum: " << sum;
}
