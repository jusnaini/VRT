/*
 Last modified: 18 Jan 2019
	- set the option for 'Manual'
	- able to set any value Bogballe calibrator [0,200]
 Date created : 20 Nov 2017
 File         : vrt_server4_1.c:
 	- send packet : "#,data1,data2,data3,data4,data5,data6"
    - recv packet : "start,pause,gstage,gpsx,gpsy,manual,apprate"
	- the jump() function replaced the prvs mechanism of goto START,PAUSE,STOP
	- the function included in every case to check the current state:
		jump() = 1 when (start = 1 && pause !=1) :printf("continue");
		jump() = 2 when (start = 1 && pause ==1) :printf("paused");
		jump() = 3 when (start !=1)              :printf("stopped");

    - cases:
		while jump() == 1
			if manual==1
				apprateTx = get apprate from client;
			if manual =!
				apprateTx = compute!
			send updated msg
		while jump() == 2
			wait until pause !=1
			send previous msg(msg not updated) 
		jump() == 3
			close udp_socket
			try to reconnect
			send empty msg

	- Remarks - Bogballe calibrator enabled
			  - data sent at auto mode(manual!=1) obtained from sensor
			  - the VI(RE,NDRE,..etc) values are averaged for Ntime
			  - select() for non-blocking not included
			  - 
	
*/
//////////////////////////////////////////////////////////////////////////////
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>     /*Unix Standard Definitions*/
#include <termios.h>    /*Posix Terminal Control Definitions*/
#include <fcntl.h>      /*File Control Definitions*/
#include <errno.h>      /*Error Number Definitions*/
#include <arpa/inet.h>
#include <sys/socket.h>
#include <time.h>
#include <stdbool.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/time.h>

#define PORT_SENSOR "/dev/ttyS5"
#define PORT_CALIBRATOR "/dev/ttyS7"
#define PORT_UDP 4445
#define BUFLEN 512
//////////////////////////////////////////////////////////////////////////////
int die (char *s)
{
    perror(s);
    exit(1);
}
/*--------------------------------------------------------------------------*/
char **parse_data(char *str_rbuf)
{
    int i=0;
    char *p = strtok(str_rbuf,",");
    char **rx_array=malloc(7*sizeof(char*));
    while(p!=NULL)
    {
        rx_array[i++] = p;
        p = strtok(NULL,",");
    }
    //for(i = 0; i<7;i++)
      //  printf("rx_array[%d]= %s\n",i,rx_array[i]);
    return rx_array;      
}
/*--------------------------------------------------------------------------*/
int jump(int start, int pause)
{
	if(start==1 && pause !=1)
	{	
		puts("Continue..");
	    return 1;
	}
	if(start == 1 && pause == 1)
	{
		puts("Paused..");
		return 2;
	}
	if(start !=1 )
	{
		puts("Stopped..");
		return 3;
	}
}
/*--------------------------------------------------------------------------*/
int csum(char *buff)
{
    int len=strlen(buff);
    if(buff[len-1]=='\n')
	buff[--len] = '\0';
    int csum=0;
    for(int i =0; i<len; i++){
	csum=csum^buff[i];}
    return csum;
}
//////////////////////////////////////////////////////////////////////////////
int port_sensor(void)
{
    int port;
    port = open(PORT_SENSOR,O_RDWR | O_NOCTTY | O_NDELAY);
    if (port <1)
	die("Unable to open port_sensor\n ");
    else
	fcntl(port,F_SETFL,0);
    return (port);
}
int sensorPortsettings(int fsensor)
{
    struct termios specs;
    /*Modify port settings*/
    cfsetospeed(&specs,B38400);
    cfsetispeed(&specs,B38400);
    specs.c_cflag |= (CS8 | CREAD | CLOCAL |CRTSCTS);
    specs.c_cflag &= ~(PARENB | CSTOPB );
    specs.c_lflag |= ICANON;
    specs.c_iflag |=  (IGNPAR | ICRNL);
    specs.c_oflag  = 0;
    specs.c_cc[VMIN] = 1;
    specs.c_cc[VTIME]= 0;
    /*Clear port line and set modified port settings*/
    tcflush(fsensor, TCIOFLUSH);
    if (tcsetattr(fsensor,TCSANOW,&specs) != 0) 
	die("tcsetattr:Unable to set sensorPortsettings");
}
//////////////////////////////////////////////////////////////////////////////
int port_calibrator(void)
{
    int port;
    port = open(PORT_CALIBRATOR,O_RDWR | O_NOCTTY | O_NDELAY);
    if (port <1)
	die("Unable to open port_calibrator port\n");
    else
	fcntl(port,F_SETFL,0);
    return (port);
}
int calibratorPortsettings (int fcal)
{
    struct termios specs;  
    /*Modify port settings*/
    cfsetospeed(&specs,B9600);
    cfsetispeed(&specs,B9600);
    specs.c_cflag |= (CS8 | CREAD | CLOCAL);
    specs.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);
    specs.c_iflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    specs.c_oflag &= ~OPOST;
    specs.c_cc[VMIN] = 1;
    specs.c_cc[VTIME]= 0;
    //--Clear port line and set modified port settings
    tcflush(fcal, TCIFLUSH);
    if (tcsetattr(fcal,TCSANOW,&specs) != 0)
	die("tcsetattr:Unable to set calibratorPortsettings");
}
//////////////////////////////////////////////////////////////////////////////
int main(void)
{
	/*==========UDP Socket Variables==========*/
    struct sockaddr_in si_me, si_other;
    int udp_socket, slen=sizeof(si_other);
    int recv_len;
    char rbuf[BUFLEN], msg[BUFLEN];  
    /*==========Crop Circle Variables==========*/
    struct termios old_sensor;
    int port_sen;
    unsigned char buf_sensor[255];
    char RE[8],NIR[8],Red[8],NDRE[8],NDVI[8];
    //float RE,NIR,Red,NDRE,NDVI;
    float ave_RE, ave_NIR, ave_Red, ave_NDRE, ave_NDVI;
    int Ncount, rdlen, loop;
	/*==========Bogballe calibrator variables==========*/
	struct termios old_calibrator;
	int port_cal;
	unsigned char buf_apprate[15];
    unsigned char str_apprate[15];
    unsigned char tmp_apprate[15];
   	/*==========Recv packet variables==========*/
	int start, pause, gstage,manual;
	float gpsx,gpsy,apprateRx;
    unsigned char apprateRx_str[15];
	/*==========Send packet variables==========*/
	char flag = '#';
    float apprateTx, gindex,volume,nitrogen,data1,data2;
    //char apprateTx[8];
    /*==========Timer for select()==========*/
	struct timeval tv;
	tv.tv_sec = 0;
    tv.tv_usec = 10000;
    fd_set rset;
    /*----------------------------------------------------------------------*/
    /*Establish Connection*/
    /*----------------------------------------------------------------------*/
    if ((udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1)
        die("Unable to create udp_socket\n");
    memset((char *)&si_me,0,sizeof(si_me));
    memset((char *)&si_other,0,sizeof(si_other));
    si_me.sin_family      = AF_INET;
    si_me.sin_port        = htons(PORT_UDP);
    si_me.sin_addr.s_addr = htonl(INADDR_ANY);

    if ((bind(udp_socket,(struct sockaddr*)&si_me,sizeof(si_me))) == -1)
        die("Unable to bind udp_socket\n");
    printf("Waiting for request..\n");
    fflush(stdout);
    /*----------------------------------------------------------------------*/
    /*Extract Client Info*/
    /*----------------------------------------------------------------------*/
	if(recv_len = recvfrom(udp_socket,rbuf,BUFLEN,0,
        (struct sockaddr*)&si_other,&slen)==-1)
        die("Unable to receive udp_socket\n");
    printf("Source : %s\n", inet_ntoa(si_other.sin_addr));
    printf("Port   : %d\n", ntohs(si_other.sin_port));
    unsigned char bograte[15];
    char **rx_array=parse_data(rbuf);
    start 		= atoi(rx_array[0]);
    pause 		= atoi(rx_array[1]);
    gstage 		= atoi(rx_array[2]);
    gpsx 		= atof(rx_array[3]);
    gpsy 		= atof(rx_array[4]);
    manual 		= atoi(rx_array[5]);
    //apprateRx 	        = atof(rx_array[6]);
    //apprateRx 		= atof(rx_array[6]);
    
    strcpy(apprateRx_str, rx_array[6]);
    //printf("Apprate received: %s",apprateRx_str); 
    //apprateRx_str = 128;
    free(rx_array);

    sprintf(bograte,"%.0f",apprateTx);

	jump(start,pause);
    printf("start:%d\npause:%d\ngstage:%d\ngps_x:%f\ngps_y:%f\nmanual:%d\
        \napprateRx:%f\n",start,pause,gstage,gpsx,gpsy,manual,apprateRx);
    puts("------------------------------------------------------------------");

    printf("START-1, STOP-0           : %d\n", start);
    printf("MANUAL-1, AUTO-0          : %d\n", manual);
    printf("PAUSE(1-enable, 0-disable): %d\n", pause);
    puts("------------------------------------------------------------------");
    /*----------------------------------------------------------------------*/
    /*System Operation*/
    /*----------------------------------------------------------------------*/
    int status = jump(start,pause);
	while(1){//the system keeps running
	if (status == 1)
	{
		/*============================================================*/
		// when start:
		// 	open sensor port;
	  	//	open calibrator port;
		// 		while start true:
		//	   		if (manual manual):
		//	 	  		set calibrator with user-defined apprate
		//	   		if(auto mode):
		//		  		compute apprate with data from crop circle
		//	   		send msg to client;
		//	   		recv fbuf from client;
		// 	close sensor port;
		//  close calibrator port;
		/*============================================================*/
		port_sen = port_sensor();
        tcgetattr(port_sen,&old_sensor); //get un-modified port settings 
        sensorPortsettings(port_sen);
        
        port_cal=port_calibrator();
        tcgetattr(port_cal,&old_calibrator); //get un-modified port settings
        calibratorPortsettings(port_cal);

		while(status == 1){
		memset(&rbuf, 0, sizeof(rbuf));
        bzero(rbuf, BUFLEN);
        memset(&msg, 0, sizeof(msg));
        bzero(msg, BUFLEN);
		if (manual == 1)
		{
			apprateTx = apprateRx;
			gindex    = 0.5;
			volume	  = 120.0;
			nitrogen  = 130.0;
			data1     = 777.7;
			data2     = 888.8;
			//sprintf(buf_apprate,"SD%s",bograte);
			//sprintf(str_apprate,"{%s%c}\r",buf_apprate,csum(buf_apprate));
			unsigned char buf_apprate[15];
            unsigned char str_apprate[15];
            unsigned char tmp_apprate[15];
            
            //buf_apprate = "124";
			//sprintf(str_apprate,"SD195");
            printf("Apprate received: %s",apprateRx_str); 
            sprintf(str_apprate,"SD%s",apprateRx_str);
	        sprintf(tmp_apprate,"{%s%c}\r",str_apprate,csum(str_apprate));
            
			/*Write data to calibarator port*/
    		if(write(port_cal,tmp_apprate,sizeof(tmp_apprate))<1)
				//die("Unable to write apprate to calibrator");
			printf("Application rate = %s",tmp_apprate);		
		}
		if (manual != 1 )
		{
			/*apprateTx = 999.9;
			gindex    = 0.2;
			volume	  = 125.0;
			nitrogen  = 135.0;
			data1     = 555.5;
			data2     = 444.4;*/
            time_t begin = time(0);
            time_t end   = time(0);
            int Ntime    = 2;
			ave_RE=0;ave_NIR=0;ave_Red=0;ave_NDRE=0;ave_NDVI=0;
            for(Ncount=0;difftime(end,begin)<Ntime;time(&end)){
			rdlen             = read(port_sen,buf_sensor,sizeof(buf_sensor));
			buf_sensor[rdlen] = 0;
            if((int)strlen(buf_sensor)> 1)
            {
                /*strcpy(RE,strtok(buf_sensor,","));
                strcpy(NIR,strtok(NULL,","));
                strcpy(Red,strtok(NULL,","));
                strcpy(NDRE,strtok(NULL,","));
                strcpy(NDVI,strtok(NULL,","));
				ave_RE  += strtof(RE,NULL);
                ave_NIR += strtof(NIR,NULL);
	            ave_Red += strtof(Red,NULL);
                ave_NDRE+= strtof(NDRE,NULL);
                ave_NDVI+= strtof(NDVI,NULL);*/
                char **tx_array = parse_data(buf_sensor);
	            ave_RE   += atof(tx_array[0]);
                ave_NIR  += atof(tx_array[1]);
                ave_Red  += atof(tx_array[2]);
                ave_NDRE += atof(tx_array[3]);
                ave_NDVI += atof(tx_array[4]);
            Ncount++;
			free(tx_array);
            }}//end read Ncount = Ntimex10 of Crop Circle data
            apprateTx = ave_RE/Ncount;
            gindex    = ave_NIR/Ncount;
            volume    = ave_Red/Ncount;
            nitrogen  = ave_NDRE/Ncount;
            data1     = ave_NDVI/Ncount;
            data2     = 999;
		}
        float app;
        app = atof(apprateRx_str);
        //printf("#SensorData = %d\n",Ncount);
		sprintf(msg,"%c,%f,%f,%f,%f,%f,%f",\
			flag,app,gindex,volume,nitrogen,data1,data2);
		//printf("Data Sent: ");
		//puts(msg);
		sendto(udp_socket,msg,sizeof(msg),0,(struct sockaddr*)&si_other,slen);
		fflush(stdout);
		recvfrom(udp_socket,rbuf,BUFLEN,0,(struct sockaddr*)&si_other,&slen);
		printf("Data Recv: ");
		puts(rbuf);

        char **rx_array=parse_data(rbuf);
        start = atoi(rx_array[0]);
        pause = atoi(rx_array[1]);
        manual = atoi(rx_array[5]);
        //apprateRx = atof(rx_array[6]);
        strcpy(apprateRx_str,rx_array[6]);
        free(rx_array);

		status = jump(start,pause);
		}//end while status=1
    tcsetattr(port_sen,TCSANOW,&old_sensor);
	close(port_sen);
	tcsetattr(port_cal,TCSANOW,&old_calibrator);
	close(port_cal);
	}
	if (status == 2)
	{
		while(status == 2){
		//sprintf(msg,"%c,%f,%f,%f,%f,%f,%f",\
			flag,apprateTx,gindex,volume,nitrogen,data1,data2);
		apprateTx=0;
		sprintf(msg,"%c,%f,%f,%f,%f,%f,%f",\
			flag,apprateTx,gindex,volume,nitrogen,data1,data2);
		memset(&rbuf, 0, sizeof(rbuf)); //clear buffer to_receive only
        bzero(rbuf, BUFLEN);
		printf("Data Sent: ");
		puts(msg); //from previous start
		sendto(udp_socket,msg,sizeof(msg),0,(struct sockaddr*)&si_other,slen);
		fflush(stdout);
		recvfrom(udp_socket,rbuf,BUFLEN,0,(struct sockaddr*)&si_other,&slen);
		printf("Data Recv: ");
		puts(rbuf);

        char **rx_array=parse_data(rbuf);
        start = atoi(rx_array[0]);
        pause = atoi(rx_array[1]);
        manual = atoi(rx_array[5]);
        //apprateRx = atof(rx_array[6]);
        strcpy(apprateRx_str,rx_array[6]);
        free(rx_array);
							
		status = jump(start,pause);
		}
	}
	if (status == 3)
	{		
		while(status == 3){
		close(udp_socket);
		memset(&rbuf, 0, sizeof(rbuf));
        bzero(rbuf, BUFLEN);
        memset(&msg, 0, sizeof(msg));
        bzero(msg, BUFLEN);

		if ((udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1)
        	die("Unable to create udp_socket\n");
    		memset((char *)&si_me,0,sizeof(si_me));
    	memset((char *)&si_other,0,sizeof(si_other));
    	si_me.sin_family      = AF_INET;
    	si_me.sin_port        = htons(PORT_UDP);
    	si_me.sin_addr.s_addr = htonl(INADDR_ANY);

    	if ((bind(udp_socket,(struct sockaddr*)&si_me,sizeof(si_me))) == -1)
        	die("Unable to bind udp_socket to reconnect");
    	printf("Waiting for request..\n");
    	fflush(stdout);

		if(recv_len = recvfrom(udp_socket,rbuf,BUFLEN,0,
           (struct sockaddr*)&si_other,&slen)==-1)
           die("Unable to receive udp_socket\n");

		char **rx_array=parse_data(rbuf);
    	start = atoi(rx_array[0]);
    	pause = atoi(rx_array[1]);
        free(rx_array);

		sprintf(msg,"%c, , , , , ,",flag);//send empty string
        sendto(udp_socket,msg,sizeof(msg),0,(struct sockaddr*)&si_other,slen);
		fflush(stdout);

		status = jump(start,pause);}
	}
}//end while(1) : the system keeps running
	return 0;
}
//////////////////////////////////////////////////////////////////////////////
