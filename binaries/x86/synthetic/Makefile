CFLAGS = -fno-PIC -fno-stack-protector -g 
CC = gcc $(CFLAGS)
NASM_64 = $(wildcard source/*.nasm64)
SOURCE_VULN = $(foreach FILE, $(NASM_64), $(FILE:.nasm64=.vuln64))
VULN_64 = $(foreach FILE, $(SOURCE_VULN), $(FILE:source%=vuln%))
SOURCE_GDT = $(foreach FILE, $(NASM_64), $(FILE:.nasm64=.gdt64))
GDT_64 = $(foreach FILE, $(SOURCE_GDT), $(FILE:source%=vuln%))

all: source/vul32.o source/vul64.o $(VULN_64) $(GDT_64)

source/vul32.o: source/vul.c
	$(CC) -m32 $< -o $@ -c

source/vul64.o: source/vul.c
	$(CC) -m64 $< -o $@ -c

source/%.on64: source/%.nasm64
	nasm -f elf64 $< -o $@

vuln/%.vuln64: source/%.on64 source/vul64.o
	$(CC) -Tvuln.script -no-pie source/vul64.o $< -o $@

vuln/%.gdt64: source/%.on64 source/vul64.o
	$(CC) -Tgdt.script -no-pie source/vul64.o $< -o $@

.PHONY:
clean:
	-rm -f vuln/*.addr vuln/*.db vuln/*.input vuln/*.output vuln/*.ropchain vuln/*.script
