import numpy
import sys
import serial
import time


SET_REF = 0x01
REQ_POS = 0x02
SEND_POS = 0x03

ERR_ID = 10
ERR_HEAD = 11
ERR_CH = 12

ID = 0x17 # unque per motor controller

def makeHead(id):
	buffr = ""
	buffr = buffr + chr(0xFF) + chr(0xFF) + chr(id)
	return buffr

def makeCheckSum(Buffr):
	d = 0
	for i in range (2,len(Buffr)):
		d = d + ord(Buffr[i])
	d = d & 0xFF
	return chr(d)

def makeReqPos(buffr):
	buffr = buffr + chr(0x02) + chr(0x02);
	Ch = makeCheckSum(buffr)
	buffr = buffr + (Ch)
	return buffr

def makeRef(ID,theta):
	buff = makeHead(ID)
	buff = buff + chr(0x04) # 4 more to read
	buff = buff + chr(0x01) # set ref
	thetaInt = int(numpy.floor(theta))# needs to be 16 bits
	#print(thetaInt)
	thetaLSB = chr(thetaInt & 0xFF)
	thetaMSB = chr((thetaInt>>8) & 0xFF)
	buff = buff + thetaMSB + thetaLSB
	buff = buff + makeCheckSum(buff)
	return buff

def getMSG():
	readBuff = serial.read()
	if(readBuff[0] != readBuff[1] != 0xFF):
		return (1,ERR_HEAD)
	tempBuff = readBuff[0:len(readBuff)-1]
	ck = makeCheckSum(tempBuff)
	if(ck != readBuff[len(readBuff) -1]):#checkSum
		return (1,ERR_CK)
	# all checks complete
	if(buff[2] != ID):
		return (1,ERR_ID) # proper messege but not to us
	
	if(buff[3] == SET_REF):
		thetaiMSB = buff[5]
		thetaiLSB = buff[6]
		thetai = int((thetaiMSB << 8) | thetaiLSB) # 16 bit
		theta = float(thetai * 1.0) * 0.005
		return (0,theta)

def sendMSG(buff):
	ser.write(buff)

def getCheck(checker):
	ck = 0
	cnt = 0;
	a = cnt + 2
	while 1:
		ck = ck + int(checker[cnt:a],16)
		#print(ck)
		#print(int(checker[cnt:a],16))
		cnt = cnt +2
		a = cnt +2
		if((cnt+2) == len(checker)):
			return ck
			

def convertMSG(inStr):
	newByte = ""
	for i in range(len(inStr)):
		a = i +2
		print(a)
		if(a == len(inStr)):
			a = a-1
		newByte= newByte + chr(int(inStr[i:a],16))
		print(newByte[i])
		#i = i+1
	return newByte	
def sendPosReq():
	curBuff = makeHead(ID)
	curBuff = makeReqPos(curBuff) #makeRef(ID, 60)#makeReqPos(curBuff)
	print("sending msg")
	sendMSG(curBuff)


ser = serial.Serial(
    port='/dev/ttyS0',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=1)

theta = input("what is the input Power")

print("connected to: " + ser.portstr)
#curBuff = makeHead(ID)
#curBuff = makeReqPos(curBuff) #makeRef(ID, 60)#makeReqPos(curBuff)
#sendMSG(curBuff)
#sendPosReq()
stop = False
curBuff = makeRef(ID,theta)
sendMSG(curBuff)
send = False
time.sleep(1)
sendPosReq()
start = time.time()
count = 0
while 1:
	#time.sleep(.2)
	try:
		if(ser.inWaiting()):
			tdata = ser.read(4)
			if(tdata):
				if(tdata[0:4] == 'FFFF'):
					tdata = ser.read(4)
					yup = tdata + ser.read(2*int(tdata[2:4],16))
					if(int(yup[10:12],16) == getCheck(yup)):
						if(int(tdata[0:2],16) == ID):#id verified
							if(int(yup[4:6],16) == SEND_POS):
								print("found")
								theat = (int(yup[6:8],16) | int(yup[8:10],16)<<8)
								#theat = theat * .005
								print(theat)
								#send = True
						else:
							print("wrong Id")
					else:
						print("check sum error")
	except:
		ser.close()
		ser = serial.Serial(
			port='/dev/ttyS0',\
			baudrate=9600,\
			parity=serial.PARITY_NONE,\
	    		stopbits=serial.STOPBITS_ONE,\
		 	bytesize=serial.EIGHTBITS,\
        		timeout=1)
		print("keep gong")
	count = count +1
