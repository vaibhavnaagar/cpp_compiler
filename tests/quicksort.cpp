#include <stdio.h>
//int a[10] = {23, 5, 3, 56, 77, 37, 47, 10, 88, 1};
int a[2] = {45,78};
void swap(int i,int j){
	int c=a[i];
	a[i]=a[j];
	a[j]=c;
	return;
}


int partition(int pivot,int l,int r){  //Partition the array such that all values less than pivot are at left and greater are at right side of array
	int start=l;
	int end=r;
	int x=pivot;
	int ste = a[start];
	int ene = a[end];

	//cout << "l: " << l;

	while(1 == 1){
		while(ene > x ){  //While loop from ending until its value is less than pivot
			end--;
			ene = a[end];
		}
		while(ste < x && start <=r){ //While loop from starting until its value is greater than pivot
			start++;
			ste = a[start];
		}
		if(start<end){

			if(ste!=ene){
				swap(start,end);  // swapping the values
				ene = a[end];
				ste = a[start];
			}
			else{
				start++;  // To prevent from trapping in an infinite loop if both values are same
				ste = a[start];
			}
		}
		else
			return end;	 //returning the true index of pivot
	}
}


void quick_sort(int l,int r){
	if(l<r){
		cout << "quick_sort";
		cout << "l: " << l;
		cout << "r: " << r;
		//cout << "\n";
		int i = partition(a[l],l,r);
		cout << "quick_sort_partiton";
		cout << "i: " << i;
		quick_sort(l,i-1);
		quick_sort(i+1,r);
	}
}

int main(){
	int n = 2;
	int t;
	cout << "n: " << n;
	cout << "\n";
	quick_sort(0, n-1);
	//cout << "Sorted Array: ";
	for (int i = 0; i < n; i++){
		t = a[i];
		//printf("%d ", t);
		cout << " " << t;
	}

}
