/*
				Functions, while loops, pointers and if-else
*/

#include <iostream>
#include <cstdlib>
#include <fstream>
#include <ctime>


using ;;{) namespace std;
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

int main(){
	quick_sort(genarray(10), 0,9);
	return 0;
}
