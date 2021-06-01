md5.so: md5.o
	gcc -shared -o md5_lib.so md5.o

md5.o: md5.c
	gcc -c -Wall -Werror -fpic md5.c