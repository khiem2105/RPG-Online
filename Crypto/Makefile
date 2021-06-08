rsa.so: rsa.o
	gcc -shared -o rsa_lib.so rsa.o

rsa.o: rsa.c
	gcc -c -Wall -Werror -fpic rsa.c