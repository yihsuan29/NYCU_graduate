#include "syscall.h"
int main(void)
{
	char test[] = "abcdefghijklmnopqrstuvwxyz";
	int success = Create("file1.test");
	OpenFileId fid;
	int i;
	if (success != 1) MSG("Failed on creating file");
	fid = Open("file1.test");	
	if (fid == -1) MSG("Failed on opening file");
	for (i = 0; i < 26; ++i) {
		int count = Write(test + i, 1, fid);
		if (count != 1) MSG("Failed on writing file");
	}
	for (i = 0; i < 26; ++i) {
		int count = Read(test + i, 1, fid);
		if (count != 1) MSG("Failed on reading file");
	}
	Halt();//我弄到這
	success = Close(fid);
	if (success != 1) MSG("Failed on closing file");
	Halt();
}

