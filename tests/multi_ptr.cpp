int main()
{
  int sum = 9;

  int *y;
  int **x;
  y = &sum;
  x = &y;
  **x = 450;

  int z;
  z = sum*100;
  z += **x + *y;
  cout << "z: " << z;
  cout << "Sum = " << sum;

  }
