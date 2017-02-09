#include <iostream>
#include <cstdlib>
#include <fstream>
#include <ctime>


using namespace std;
#define N 7


int count;


int* genarray(int n){
	int i=0;
	int* a= new(nothrow) int[n];
	srand((unsigned)time(0));
	for (int i = 0; i < n; ++i)
	{
		a[i]=rand()%10000000;
	}
	return a;
}


void swap(int* a,int i,int j){
	int c=a[i];
	a[i]=a[j];
	a[j]=c;
	return;
}


int partition(int* a,int pivot,int l,int r){
	int start=l;
	int end=r;
	int x=pivot;
	while(1){
		while(a[end] > x ){
		//	count++;
			end--;	
		}
		while(a[start] < x && start <=r){
		//	count++;
			start++;
		}
		if(start<end){
			if(a[start]!=a[end])
				swap(a,start,end);
			else
				start++;
		}
		else
			return end;	
	}
}


void quick_sort(int* a,int l,int r){
	if(l<r){ 
		int i = partition(a,a[l],l,r);
		quick_sort(a,l,i-1);
		quick_sort(a,i+1,r);
	}
	return;
}



int select(int* a,int i,int l, int r){
	int size=r-l+1;
	if(size==1)
		return a[l];
	int* m;
	if(size%N ==0)
		m= new int[size/N];
	else
		m= new int[size/N +1];
	int j;
	int p=0;
	for(j=l;j<=r;j+=N){
		if(r-j+1>=N){
			quick_sort(a,j,j+N-1);
			m[p++]=a[j+N/2];
		}
		else{
			quick_sort(a,j,r);
			m[p++]=a[j+(r-j)/2];
		}
	}
	int x= select(m,p/2,0,p-1);	
	int k= partition(a,x,l,r);
	if(i==k)
		return x;
	else if(i<k)
		return select(a,i,l,k-1);
	else
		return select(a,i,k+1,r);
}


int main(){
	ofstream myfile;
	myfile.open("medians7.txt");
	int* a;
	int n=1;
	int i,j;
	int med=0;
	clock_t start,end;
	double run_time,total_time, avg_time;
	total_time=0.0;
	cout <<"th";
	for(n=1;n<=1000000;n*=2){
		for(j=0;j<100;j++){
			a=genarray(n);
			start=clock();
			med=select(a,n/2,0,n-1);
			end=clock();
			run_time= ((end-start))/(double) CLOCKS_PER_SEC;
			total_time+= run_time;
		}
		avg_time=total_time/100;
		myfile << n << " " << avg_time << endl;
		total_time=0.0;

	}
	myfile.close();
	return 0;
}