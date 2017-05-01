#include<cstdio>


int ackermann(int x, int y)
{
	if(x<0 || y<0)
		return -1;
	if(x==0)
		return y+1;
	if(y==0)
		return ackermann(x-1,1);
	return ackermann(x-1,ackermann(x,y-1));
}

int main(int argc, char **argv)
{
	int x,y;
	x = 3;
	y = 4;
	int output = ackermann(x,y);
	printf("%d", output);
	//cout << "ackermann" << output;
}