CC = gcc
ORIG_BINS = $(wildcard orig/*/*)
VULN_BINS = $(foreach FILE, $(ORIG_BINS), $(FILE:orig%=vuln%))

all: $(VULN_BINS)

source/vul64.o: source/vul.c
	$(CC) -m64 $< -o $@ -fno-PIC -fno-stack-protector -g -c

vuln/%/:
	mkdir -p $@

orig/%.merg_o: orig/%.bin source/vul64.o
	objcopy --add-section .mytext=$< --set-section-flags .mytext=alloc,code,load,readonly source/vul64.o $@

vuln/%.bin: orig/%.merg_o
	mkdir -p $(dir $@)
	$(CC) -m64 -g -no-pie -fno-PIC $< -o $@

.PHONY:
clean:
	find . -name "*.o" -delete
	find . -name "*.merg_o" -delete
	find . -name "*.ropchain" -delete
	find . -name "*.input" -delete
	find . -name "*.output" -delete
	find . -name "*.script" -delete
	find . -name "*.addr" -delete
	find . -name "*.db" -delete
