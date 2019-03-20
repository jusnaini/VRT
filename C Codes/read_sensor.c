/*
VERSION   : 1 (2/5/2017)
OPERATION : Grab serial data from port and display on screen 
*/

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <stdlib.h>

int die(char *s)
{
    perror(s);
    return(-1);
}

int set_interface_attribs (int fd, int speed)
{
    struct termios options;
  
    /*Get current serial port settings*/
    if(tcgetattr(fd,&options)<0)
        die("tcgetattr::Unable to get port settings\n");
    /*--------------------*/
    /*Modify port settings*/ //Noparity,8bits,1stopbit
    /*--------------------*/
    cfsetispeed(&options, (speed_t)speed); //B38400
    cfsetospeed(&options, (speed_t)speed); //B38400
    /*control options*/
    options.c_cflag |=  ( CS8 |CLOCAL | CREAD | CRTSCTS );
    options.c_cflag &= ~(PARENB | CSTOPB); //no parity, 1 stop bit
    /*line options*/
    options.c_lflag |= (ICANON);
    /*output options*/
    options.c_oflag = 0;
    /*input options*/
    options.c_iflag |=  (IGNPAR | ICRNL);
    /*control characters*/
    options.c_cc[VMIN]  = 1;
    options.c_cc[VTIME] = 0;
    
    /*clean modem line and activate port settings*/
    tcflush(fd,TCIFLUSH);
    if (tcsetattr(fd, TCSANOW, &options) != 0) 
       die("tcsetattr::Unable to set port settings\n");
    return(-1);
}

int main(void)
{
    char *portname = "/dev/ttyS8";
    int fd, rdlen;
    unsigned char buf[255];
    struct termios old_sensor; //to get previous settings
    
    /*Open port*/
    fd = open(portname, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0)
	die("open_port: Unable to open /dev/ttyS7 \n");
    else
	fcntl(fd,F_SETFL,0);
    
    /*get and set the options*/
    tcgetattr(fd,&old_sensor); //save old port settings
    set_interface_attribs(fd,B38400);

    /*simple noncanonical input*/
    memset(buf,'\0',sizeof(buf));
    do{
	rdlen = read(fd,buf,sizeof(buf));
	buf[rdlen]= 0; //to skip space after string data rcv from sensor

	if((int)strlen(buf)>1){
	   //printf("Read %d: %s\n",rdlen,buf);
	   puts(buf);
	}
	sleep(0.5);
	
      }while(1);
/*Restore old port settings*/
tcsetattr(fd,TCSANOW,&old_sensor);

/*Close port*/
close(fd);
return 0;
}	
