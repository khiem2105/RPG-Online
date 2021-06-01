#include "md5.h"

unsigned int F(unsigned int ABCD[4])
{
	unsigned int calcul;
	calcul = (ABCD[1] & ABCD[2]) | (~ABCD[1] & ABCD[3]);
	return calcul;
}

unsigned int G(unsigned int ABCD[4])
{
	unsigned int calcul;
	calcul = (ABCD[1] & ABCD[3]) | (ABCD[2] & (~ABCD[3]) );
	return calcul;
}

unsigned int H(unsigned int ABCD[4])
{
	unsigned int calcul;
	calcul = (ABCD[1] ^ ABCD[2]) ^ ABCD[3];
	return calcul;
}

unsigned int I(unsigned int ABCD[4])
{
	unsigned int calcul;
	calcul = (ABCD[2] ^ (ABCD[1] | (~ABCD[3]) ) );
	return calcul;
}

//Use binary integer part of the sines of integers (Radians) as constants:
unsigned int *calctable( unsigned *k)
{
    double a, b;
    int i;

    b = pow( 2, 32);
    for (i = 0; i < 64; i++)
    {
        a = fabs(sin(i + 1));
        k[i] = floor( a * b );
    }
    return k;
}

unsigned int leftrotate(unsigned int x,unsigned int n) {
  return (x << n) | (x >> (32 -n));
}

char* md5(char * message)
{
	int i,j;
	static unsigned *K;
	static unsigned kspace[64];
	K = calctable(kspace);
	//s specifies the per-round shift amounts
    int s[64] = {
         7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,//s[0..15]
         5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,//s[16..31]
         4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,//s[32..47]
         6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21 //s[48..63]
				};
	// initial variables a0 b0 c0 d0
	unsigned int a0 = 0x67452301;
	unsigned int b0 = 0xefcdab89;
	unsigned int c0 = 0x98badcfe;
	unsigned int d0 = 0x10325476;

	//calculate length of message in byte and bit
	unsigned long long lengBits = strlen(message) * 8 ;
	unsigned long long lengBytes = strlen(message);

	unsigned char * clengBits = (unsigned char *) &lengBits;
	//unsigned char * clengBytes = (unsigned char *) &lengBytes;

	//plus 1 and then modulo 512 (in bits)
	int sizePlus1 = (strlen(message) + 1) % 64;

	//padding require 56 - sizePlus1   (as we need 64 bits left)

	//length of message after padding
	unsigned long long lengPaddedBytes = strlen(message)+1+56-sizePlus1 + 8;
	unsigned char * paddedMess = (unsigned char*) calloc(lengPaddedBytes,1);

	for (i = 0; i < lengBytes; i++)
	{
		*(paddedMess + i) = (unsigned char) *(message + i);
	}

	paddedMess[lengBytes] = 0x80;


	//fill the 64 bits left
	for(i = lengPaddedBytes - 8; i < lengPaddedBytes; i++)
	{
        paddedMess[i] = *(clengBits + i % 8);
	}

	unsigned int* paddedMess_ = (unsigned int*) paddedMess;
	unsigned int ABCD[4];
	unsigned int ret,g;
	for(i = 0; i < lengPaddedBytes / 64; i++)
	{
		ABCD[0] = a0;
		ABCD[1]	= b0;
		ABCD[2] = c0;
		ABCD[3]	= d0;

		for (j = 0 ; j <=63 ; j++)
		{

			if(j<16)
			{
				ret = F(ABCD);
				g = j;
				//printf("\n ---- ret = %i", ret);
			}
			else if (j <= 31)
			{
				ret = G(ABCD);
				g = (5 * j +1) % 16;
				//printf("\n ---- ret = %i", ret);
			}
			else if (j<=47)
			{
				ret  = H(ABCD);
				g = (3 * j + 5) % 16;
				//printf("\n ---- ret = %i", ret);
			}
			else
			{
				ret = I(ABCD);
				g = (7 * j) % 16;
				//printf("\n ---- ret = %i", ret);
			}

		ret = ret + ABCD[0] + K[j] + paddedMess_[i*16 + g];
		ABCD[0] = ABCD[3];
		ABCD[3] = ABCD[2];
		ABCD[2] = ABCD[1];
		ABCD[1] = ABCD[1] + leftrotate(ret, s[j]);
		}
		a0 = a0 + ABCD[0];
        b0 = b0 + ABCD[1];
        c0 = c0 + ABCD[2];
		d0 = d0 + ABCD[3];
	}

	unsigned char dgt[16];
	dgt[0]=a0&0xff;
	dgt[1]=(a0>>8)&0xff;
	dgt[2]=(a0>>16)&0xff;
	dgt[3]=(a0>>24)&0xff;
	dgt[4]=b0&0xff;
	dgt[5]=(b0>>8)&0xff;
	dgt[6]=(b0>>16)&0xff;
	dgt[7]=(b0>>24)&0xff;
	dgt[8]=c0&0xff;
	dgt[9]=(c0>>8)&0xff;
	dgt[10]=(c0>>16)&0xff;
	dgt[11]=(c0>>24)&0xff;
	dgt[12]=d0&0xff;
	dgt[13]=(d0>>8)&0xff;
	dgt[14]=(d0>>16)&0xff;
	dgt[15]=(d0>>24)&0xff;
	char *initial = (char*)malloc(32 * sizeof(char));
	memset(initial, '\0', 32*sizeof(char));
	char *result = initial;
	for(i=0;i<16;i++)
	{
		sprintf(initial,"%02x",dgt[i]);
		initial = initial + 2;
	}
	result[32] = '\0';
	return result;
}