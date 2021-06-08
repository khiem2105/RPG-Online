#include "rsa.h"

long long Rand(long long l, long long h)
{
    return l + ((long long)rand() * (RAND_MAX ) * (RAND_MAX ) * (RAND_MAX ) +
                (long long)rand() * (RAND_MAX ) * (RAND_MAX ) +
                (long long)rand() * (RAND_MAX ) +
                rand()) % (h - l + 1);
}



//this function will generate a prime number between 2^n and 2^n-1
long generatePrime(int n)
{
	long long prime = -1;
	int k=1;
	while(k)
	{
		prime = Rand(pow(2,n-1),pow(2,n));
		if (isPrime(prime))
			k=0;
	}
	return prime;
}
//function to find gcd of 2 numbers a, b
long gcd(long a, long b){
    // if a = 0 => gcd(a,b) = b
    // if b = 0 => gcd(a,b) = a
    if (a == 0 || b == 0){
        return a + b;
    }
	// Repeat until a=0 or b=0
    while (a*b != 0){
        if (a > b){
            a %= b; // a = a % b
        }else{
            b %= a;
        }
    }
    return a + b; // return a + b, as at this time, we have a=0 or b=0
}
//function generate a coprime number of a
int coprime(long a)
{
    int co;
    do{
    		co = rand()%a;
    	}while(gcd(co, a) != 1);
    return co;
}
//function check if a number is prime or not
long isPrime(int num)
{
    if (num < 2)
        return 0;

    for (int i = 2; i <= sqrt((float)num); i ++)
    {
        if (num%i==0)
        {
            return 0;
        }
    }
    return 1;
}

key initKey(long value1, long value2) {
    key k;

    k.value1 = value1;
    k.value2 = value2;

    return k;
}

key_pair generateKey() {
	srand((long long)time(0));

	long q = 0, n = 0, phi = 0, e = 0, d = 0;
	long p = generatePrime(10);
	int k=1;
	while(k)
	{
		q = generatePrime(10);
		if (q != p)
			k=0;
	}
	n = p * q;
	phi = (p-1)*(q-1);
	e = coprime(phi);

	d = 1;
	while (((d*e) % (phi)) != 1)
	{
		d++;
	}
	
    // pair.pub_key = initKey(n, e);
    // pair.priv_key = initKey(n, d);
    key_pair pair = { initKey(n, d), initKey(n, e) };

	return pair;
}

char* itoa(long long val, int base){

    static char buf[32] = {0};

    int i = 30;

    for(; val && i ; --i, val /= base)

        buf[i] = "0123456789abcdef"[val % base];

    return &buf[i+1];

}

char* encrypt(char* msg, key Pub)
{	
	unsigned long long buf[MAX_SIZE_MESSAGE];
	memset(buf,0,MAX_SIZE_MESSAGE * sizeof(unsigned long long));
	unsigned long long temp;
	unsigned long long r;
	int i,j, len =strlen(msg);
	for (i = 0; i < len; i++)
	{
		// printf("Message[%d]: %c\n", i, msg[i]);
		buf[i] = msg[i];
		// printf("Buf[%d]: %ld\n", i, buf[i]);
	}	
	i = 0;
	while(buf[i] != 0)
	{
		r = 1;
		for(j=0;j<Pub.value2;j++)
		{
		    temp=0;
            	    temp= r*buf[i];
            	    r =temp% Pub.value1;
		}
		buf[i] = r;
		i++;
	}
	char *str = (char*)malloc(sizeof(char) * 8096);
	memset(str, '\0', 8096*sizeof(char));
	char str2[8096];
	int lenS; 
	for(i=0;buf[i]!=0;i++)
	{
		// printf("Buf[%d]: %lld\n", i, buf[i]);
		sprintf(str2, "%lld", buf[i]);
		lenS = strlen(str2);
		str2[lenS] = '\0';
		strcat(str,str2);
		strcat(str,".");
	}
	return str;
}

char* decrypt(char* str, key Priv)
{
	unsigned long long buf[MAX_SIZE_MESSAGE];
	memset(buf,0,MAX_SIZE_MESSAGE * sizeof(unsigned long long));
	int i,j;
	unsigned long long r,temp;
	unsigned long long ret=1;
	char * ptr1, * ptr2;
	ptr1 = str;

	i = 0;
	while(ret != 0)
	{
		ret = strtol(ptr1,&ptr2,10);
		// printf("Number part: %ld, String part: %s\n", ret, ptr2);
		buf[i] = ret;
		ptr1 = ptr2;
		ptr1 = ptr1+1;
		i++;
	}
	i = 0;
	while(buf[i] !=0)
	{
		r = 1;
		for(j=0;j<Priv.value2;j++)
		{
		    temp=0;
		    temp= r*buf[i];
            	    r =temp% Priv.value1;
		}
		buf[i] = r;
		i++;
	}

	char *new_str = malloc(sizeof(char) * MAX_SIZE_MESSAGE);
	for(i = 0; buf[i] != 0; i++) {
		new_str[i] = buf[i];
	}

	new_str[i] = '\0';
	// printf("Encoded string: %s, Decoded string: %s\n", str, new_str);
	return new_str;
}
















