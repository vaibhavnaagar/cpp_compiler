#include<stdio.h>

void printInorder(int start,int end);
void printPostorder(int start,int end);
void printPreorder(int start,int end);


int arr[7] = {4, 2, 6, 1, 3, 5, 7};
int arr_size = 7;

int main()
{
  cout<<"The PreOrder Traversal is:\n";
  //printf("The InOrder Traversal is: \n");
  printPreorder(0, arr_size-1);

  cout << "\n";

  cout<<"The InOrder Traversal is:\n";
  //printf("The InOrder Traversal is: \n");
  printInorder(0, arr_size-1);

  cout << "\n";

  cout<<"The PostOrder Traversal is:\n";
  //printf("The InOrder Traversal is: \n");
  printPostorder(0, arr_size-1);
  return 0;
}

void printInorder(int start,int end)
{
  if(start > end){
    return;
  }
  int val;
  /*Printing the left subtree*/
  printInorder(start*2+1,end);

  /*printing present value*/
  val = arr[start];
  cout << val << " ";
  //printf("%d ", a[start]);
  /*Printing the right subtree*/
  printInorder(start*2+2,end);
}

void printPostorder(int start,int end)
{
  if(start > end){
    return;
  }
  int val;
  /*Printing the left subtree*/
  printInorder(start*2+1,end);
  /*Printing the right subtree*/
  printInorder(start*2+2,end);

  /*printing present value*/
  val = arr[start];
  cout << val << " ";
  //printf("%d ", a[start]);
}

void printPreorder(int start,int end)
{
  if(start > end){
    return;
  }
  int val;
  /*printing present value*/
  val = arr[start];
  cout << val << " ";
  //printf("%d ", a[start]);

  /*Printing the left subtree*/
  printInorder(start*2+1,end);
  /*Printing the right subtree*/
  printInorder(start*2+2,end);
}
