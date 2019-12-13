CC = gcc
ORIG_BINS = $(wildcard orig/*/*)
VULN_BINS = $(foreach FILE, $(ORIG_BINS), $(FILE:orig%=vuln%))

all: $(VULN_BINS)

source/vul.o: source/vul.c
	$(CC) $< -o $@ -fno-PIC -fno-stack-protector -g -c

vuln/%/:
	mkdir -p $@

orig/%.exec_o: orig/%.bin
	objcopy $< $@ --only-section=.init --only-section=.text --only-section=.MIPS.stubs --only-section=.fini -S

orig/%.merg_o: orig/%.exec_o source/vul.o
	objcopy --add-section .mytext=$< --set-section-flags .mytext=alloc,code,load,readonly source/vul.o $@

vuln/%.bin: orig/%.merg_o
	mkdir -p $(dir $@)
	$(CC) -g -no-pie -fno-PIC $< -o $@

.PHONY:
clean:
	find . -name "*.o" -delete
	find . -name "*.merg_o" -delete
	find . -name "*.exec_o" -delete
	find . -name "*.ropchain" -delete
	find . -name "*.input" -delete
	find . -name "*.output" -delete
	find . -name "*.script" -delete
	find . -name "*.addr" -delete
	find . -name "*.db" -delete
