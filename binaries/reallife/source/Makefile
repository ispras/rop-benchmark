CC = gcc

all: vul32.o vul64.o

vul32.o: vul.c
	$(CC) -m32 $< -o $@ -fno-PIC -fno-stack-protector -g -c

vul64.o: vul.c
	$(CC) -m64 $< -o $@ -fno-PIC -fno-stack-protector -g -c

.PHONY:
clean:
	-rm -f *.o
