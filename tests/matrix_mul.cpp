#include<stdio.h>

int main()
{
    int N = 4;
    int A[4][4] = { {1, 1, 1, 1},
                    {2, 2, 2, 2},
                    {3, 3, 3, 3},
                    {4, 4, 4, 4}};

    int B[4][4] = { {1, 1, 1, 1},
                    {2, 2, 2, 2},
                    {3, 3, 3, 3},
                    {4, 4, 4, 4}};

    int C[4][4]; // To store result

    int i, j, k;
    for (i = 0; i < N; i++)
    {
        for (j = 0; j < N; j++)
        {
            C[i][j] = 0;
            for (k = 0; k < N; k++)
                C[i][j] += A[i][k]*B[k][j];
        }
    }

    //printf("Result matrix is \n");
    int t;
    cout << "Result matrix is \n";
    for (i = 0; i < N; i++)
    {
        for (j = 0; j < N; j++){
           //printf("%d ", C[i][j]);
           t = C[i][j];
           cout << " " << t;
        }
        //printf("\n");
        cout << "\n";
    }

    return 0;
}
