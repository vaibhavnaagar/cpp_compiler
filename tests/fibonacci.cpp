int main(){
	int a = 0;
	int b = 1;
	int c, i;
	int n = 1;
  for (i = 2; i <= n; i++)
  {
     c = a + b;
     a = b;
     b = c;
  }
  cout << c;
}