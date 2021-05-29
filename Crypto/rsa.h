#include <stdlib.h>
#include<stdio.h>
#include<time.h>
#include<math.h>
#include<string.h>

#define MAX_SIZE_MESSAGE 1024

// Useful new data type
typedef struct
{
	long value1;
	long value2;
} key;

typedef struct {
	key priv_key;
	key pub_key;
} key_pair;

// Function declaration
long generatePrime(int n);
long gcd(long a, long b);
int coprime(long a);
long isPrime(int num);
long long Rand(long long l, long long h);
key initKey(long value1, long value2);
key_pair generateKey();
char* encrypt(char * msg, key pub_key);
char* decrypt(char * msg, key priv_key);