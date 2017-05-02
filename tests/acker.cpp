#include<cstdio>

int count = 0;

int ackermann(int x, int y)
{
	count++;
	cout  << "x: " << x;
	cout  << "y: " << y;
	cout << "count: " << count;
	cout << "\n";
	if(x<0 || y<0){
		return -1;
	}
	if(x==0){
		return y+1;
	}
	if(y==0){
		return ackermann(x-1,1);
	}
	return ackermann(x-1,ackermann(x,y-1));
}

int main()
{
	int x,y;
	x = 3;
	y = 3;
	int output = ackermann(x,y);
	//printf("%d", output);
	cout << "ackermann: " << output;
}
