#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>

#ifdef WINDOWS
#include <windows.h>
#define read _read
#define sleep Sleep
#else
#include <unistd.h>
#endif

void sys(char *s) {
  printf("   SUCCESS\n");
  printf(" * Hijacked call of sys function\n");
  if (s[0] == '/' && s[1] == 'b' && s[2] == 'i' && s[3] == 'n' &&
      s[4] == '/' && s[5] == 's' && s[6] == 'h' && s[7] == 0)
    printf("   PARAMETERS ARE CORRECT\n");
  else
    printf("   !!!INCORRECT PARAMETERS!!!\n");
  printf(" * Everything is OK\n");
  return;
}

int filesize(int fd) {
  struct stat st;
  int ret = fstat(fd, &st);
  assert(ret == 0);
  return st.st_size;
}

void vul(char *filename) {
  char buf[1];
  int fd = open(filename, O_RDONLY);
  assert(fd != -1);
  size_t size = filesize(fd);
  printf("\t- File '%s' with size '%i'\n", filename, size);
  int ret = read(fd, buf, size);
  assert(ret != -1);
#ifdef WINDOWS
  ;
#else
  close(fd);
#endif
  return;
}

int main(int argc, char **argv) {
  setbuf(stdout, NULL);
  if (argc == 1) {
    sleep(5);
    return 0;
  }
  assert(argc == 2);

  int var[1000];
  var[999] = 1;
  char *filename = argv[1];

  // It is also initialize got.plt entry with actual value.
  // Without this call printf from sys function seagfults.
  printf("Start Test Program!\n");
  printf("main: %p", main);
  vul(filename);
  printf("   FAIL\n");
  printf(" * Control flow wasn't be hijacked\n");
  return 0;
}
