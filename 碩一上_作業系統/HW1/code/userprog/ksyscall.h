/**************************************************************
 *
 * userprog/ksyscall.h
 *
 * Kernel interface for systemcalls 
 *
 * by Marcus Voelp  (c) Universitaet Karlsruhe
 *
 **************************************************************/

#ifndef __USERPROG_KSYSCALL_H__ 
#define __USERPROG_KSYSCALL_H__ 

#include "kernel.h"
#include "synchconsole.h"
#include "syscall.h"


void SysHalt()
{
  kernel->interrupt->Halt();
}

int SysAdd(int op1, int op2)
{
  return op1 + op2;
}

int SysCreate(char *filename)
{
	// return value
	// 1: success
	// 0: failed
	return kernel->interrupt->CreateFile(filename);
}

/*Open -----------------------------------------------------------------------*/
OpenFileId SysOpen(char *filename) {
	// return value
	// fileId: sucess
	// -1: failed
    return (OpenFileId) kernel->interrupt->Open(filename);
}

/*Write -----------------------------------------------------------------------*/
int SysWrite(char *text, int size, OpenFileId fid){
	return kernel->interrupt->WriteFile(text,size,fid);
}
/*Read--------------------------------------------------------------------*/
int SysRead(char *text, int size, OpenFileId fid){
	return kernel->interrupt->ReadFile(text,size,fid);
}
/*Close-------------------------------------------------------------------*/
int SysClose(OpenFileId fid){
	return kernel->interrupt->Close(fid);
}
/*PrintInt---------------------------------------------------------------------*/
void SysPrintInt(int number ){  
    return kernel->interrupt->PrintInt(number);
} 


#endif /* ! __USERPROG_KSYSCALL_H__ */
