#include "xlCANFunction.h"
#include <iostream>
#include <stdio.h>

using namespace std;

int g_BaudRate = 5000000;
XLhandle g_hMsgEvent;
XLhandle g_hTxEvent;
XLportHandle g_xlPortHandle;
int g_XlTimer_Count = 0;

xlCANFunction::xlCANFunction(char* appName, int channelIndex)
{
	strcpy_s(g_AppName, "xlCANcontrol");
	channel = channelIndex;
	g_xlPermissionMask = -1;
	g_xlChannelMask = -1;
	g_xlChannelIndex = -1;
	g_hTxEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
}

xlCANFunction::~xlCANFunction()
{
	strcpy_s(g_AppName, "");
	channel = -1;
	g_xlPermissionMask = -1;
	g_xlChannelMask = -1;
	g_xlChannelIndex = -1;
}

XLstatus xlCANFunction::CANInit()
{
	XLstatus xlStatus;
	xlStatus = xlOpenDriver();
	if (xlStatus != XL_SUCCESS)
	{
		printf("Error Occur xlOpenDriver, %s\n", xlGetErrorString(xlStatus));
		system("pause");
	}
	canInit();

	xlStatus = xlActivateChannel(g_xlPortHandle, g_xlChannelMask, XL_BUS_TYPE_CAN, XL_ACTIVATE_RESET_CLOCK);
	if (xlStatus != XL_SUCCESS)
	{
		printf("Error Occur xlActivateChannel, %s\n", xlGetErrorString(xlStatus));
		system("pause");
	}

	xlStatus = xlSetTimerRate(g_xlPortHandle, 100);
	if (xlStatus != XL_SUCCESS)
	{
		printf("Error Occur xlSetTimerRata, %s\n", xlGetErrorString(xlStatus));
		system("pause");
	}

	return xlStatus;
}

XLstatus xlCANFunction::canInit()
{
	XLstatus xlStatus;
	unsigned int HwType;
	unsigned int HwIndex;
	unsigned int HwChannel;
	xlStatus = xlGetApplConfig(g_AppName, channel, &HwType, &HwIndex, &HwChannel, XL_BUS_TYPE_CAN);
	if (xlStatus != XL_SUCCESS)
	{
		printf("Error Occur xlGetApplConfig, %s\n", xlGetErrorString(xlStatus));
		system("pause");
	}
	g_xlChannelIndex = xlGetChannelIndex(HwType, HwIndex, HwChannel);
	g_xlChannelMask = xlGetChannelMask(HwType, HwIndex, HwChannel);

	g_xlChannelMask |= g_xlChannelMask;

	g_xlPermissionMask = g_xlChannelMask;

	xlStatus = xlOpenPort(&g_xlPortHandle, g_AppName, g_xlChannelMask, &g_xlPermissionMask, RX_QUEUE_SIZE, XL_INTERFACE_VERSION, XL_BUS_TYPE_CAN);
	if (xlStatus == XL_SUCCESS && g_xlPortHandle != XL_INVALID_PORTHANDLE)
	{
		xlStatus = xlCanSetChannelBitrate(g_xlPortHandle, g_xlChannelMask, g_BaudRate);
		if (xlStatus != XL_SUCCESS)
		{
			printf("Error Occur xlCanSetChannelBitrate, %s\n", xlGetErrorString(xlStatus));
			system("pause");
		}
	}
	else
	{
		xlClosePort(g_xlPortHandle);
		g_xlPortHandle = XL_INVALID_PORTHANDLE;
		printf("Error Occur xlOpenPort, %s\n", xlGetErrorString(xlStatus));
		system("pause");
	}
	return xlStatus;
}



XLstatus xlCANFunction::CANSendMsg(XLevent xlEvent, int channel)
{
	XLstatus xlStatus = XL_ERROR;
	unsigned int count = 1;
	if (xlEvent.tag == XL_TRANSMIT_MSG)
		xlStatus = xlCanTransmit(g_xlPortHandle, g_xlChannelMask, &count, &xlEvent);
	return xlStatus;
}

XLstatus xlCANFunction::canCreateRxThread()
{
	XLstatus xlStatus = XL_ERROR;
	DWORD RxThreadId = 0;

	if (g_xlPortHandle != XL_INVALID_PORTHANDLE)
	{
		xlStatus = xlSetNotification(g_xlPortHandle, &g_hMsgEvent, 1);

		g_RxThread = CreateThread(0, 0x1000, RxThread, (LPVOID)0, 0, &RxThreadId);
	}
	return xlStatus;
}

DWORD WINAPI RxThread(LPVOID par)
{
	XLstatus xlStatus;

	unsigned int msgsrx = 1;
	XLevent xlEvent;

	while (1)
	{
		WaitForSingleObject(g_hMsgEvent, INFINITE);
		
		xlStatus = xlReceive(g_xlPortHandle, &msgsrx, &xlEvent);

		if (xlStatus != XL_ERR_QUEUE_IS_EMPTY)
		{
			switch (xlEvent.tag)
			{
			case XL_TIMER_EVENT:
				SetEvent(g_hTxEvent);
				g_XlTimer_Count++;
				break;
			case XL_RECEIVE_MSG:
				break;
			default:
				break;
			}
		}
	}
	return NO_ERROR;
}

DWORD WINAPI TxThread(LPVOID par)
{
	XLstatus xlStatus;
	XLevent xlEvent;
	WaitForSingleObject(g_hTxEvent, INFINITE);


	return NO_ERROR;
}

void xlCANFunction::FillMsgData(){
	
}