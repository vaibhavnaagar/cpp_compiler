
int even(int);
int odd(int);


int even(int n){
  if (n==0){
    return 1;
  }
  else{
    return odd(n-1);
  }
}


int odd(int n){
  if (n==0){
    return 0;
  }
  else{
    return even(n-1);
  }
}

int main(){
  int n = 1001;
  cout << "N: " << n;
  cout << "\n";
  int output;
  output = even(n);
  cout << "even: " << output;
  cout << "\n";
  output = odd(n);
  cout << "odd: " << output;

}
