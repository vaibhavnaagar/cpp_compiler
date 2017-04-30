/*
int main()
{
  int y;
  float z;
  char c;
  int *pt;
  int x = 4;
  //x = y;
  y = x + x;
  z = 2.3;
  c = 'm';
	for(;x >0; x=x-1){
	cout << "hello" << y ;
	cout << c;
	cout << "\n";
	}
}*/

/*
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
*/

/*
int p = 9;
char letter = 'a';
char name[2] = "C";
float* f;
double d = 2.457;
*/

int test(int x, int y)
 {
 	int z[2] = {1,9};
 	z[1] = 7;
 	return z[1];
 }

int main()
{
  int c[3] = {3,4,5};
  int i = 2;
  int sum = 0;
  while (i>0)
  {
  	c[i] = i;
  	sum =  sum + c[i];
  	i--;
  	sum = test(i,sum) ;


  }
  cout << "Sum = " << sum;
	return 0;
 }

/* int test(int , int );

*/
/*
int main()
{
  //char c[5] = "hell";
	int a= 'e';
	if (a==1 && a > 0){
		int m;
	}
  char c;
  float f;
  cout << "hello" << a << c << f << 12.4 ;
 	return 1;
}*/
/*
 int test(int x, int y)
 {int p,q;
 	x =6;
 	return 1;
 }

 /*



  int x,y;
	x = 3 + 2*x;
	x++;
	x = y++;
	//if((x == 1) && (y==2))
	if(x==0)
	{


		m++;
			if(x<4)
			{
				m =0;
				int l;
				if(56 !=2)
				{
					l++;
					l=m+x;
				}
				l = 0;
			}*/
