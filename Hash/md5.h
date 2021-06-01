#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<string.h>
#include<unistd.h>
#define MAX_STR_SZ 2048

/* definition of 4 functions F G H I
F(X,Y,Z)=(X&Y)|(-X&Z)
G(X,Y,Z)=(X&Z)|(Y&-Z)
H(X,Y,Z)=(X^Y^Z)      ^:XOR
I(X,Y,Z)=(Y^(X|-Z))
 */

unsigned int F(unsigned int ABCD[4]);
unsigned int G(unsigned int ABCD[4]);
unsigned int H(unsigned int ABCD[4]);
unsigned int I(unsigned int ABCD[4]);
unsigned int* calctable(unsigned *k);
unsigned int leftrotate(unsigned int x, unsigned int n); //left rotate operand
char* md5(char *message);