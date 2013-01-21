#!/usr/bin/python
import serial
#import serial.tools
#print 'available ports'
#serial.tools.list_ports


def serial_test(device, time_out, bytes_read, flowcontrol = 'none'):
    '''listens to serial port [device] and prints out N [bytes_read] with timeout [time_out]'''
    try:
        ser = serial.Serial(device, 4800, parity=serial.PARITY_ODD, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=time_out)
        if flowcontrol == 'software':
            ser.xonxoff = 1
        elif  flowcontrol == 'hardware':
            ser.rtscts = 1
        buffer_input = ser.read(bytes_read)
        ser.close()
        print 'received:' + buffer_input
        if len(buffer_input) == 0:
            print 'there was no input'
        else:
            print 'Input was:' + buffer_input
    except serial.SerialException:
        print 'could not open serial device'
        pass


print 'ttyS0, test 1, 10 second timeout '
serial_test('/dev/ttyS0',10,10)
print 'ttyS1, test 1, 10 second timeout '
serial_test('/dev/ttyS1',10,10)



print 'ttyF0, test 1, 10 second timeout '
serial_test('/dev/ttyF0',10,100)
print 'ttyF1, test 1, 10 second timeout '
serial_test('/dev/ttyF1',10,100)
print 'ttyF0, test 2, 30 second timeout '
serial_test('/dev/ttyF0',30,100)
print 'ttyF1, test 2, 30 second timeout '
serial_test('/dev/ttyF1',30,100)
print 'ttyF0, test 3, 30 second timeout, software flowcontrol '
serial_test('/dev/ttyF0',30,100,'software')
print 'ttyF1, test 3, 30 second timeout, software flowcontrol '
serial_test('/dev/ttyF1',30,100,'software')
print 'ttyF0, test 4, 30 second timeout, hardware flowcontrol '
serial_test('/dev/ttyF0',30,100,'hardware')
print 'ttyF1, test 4, 30 second timeout, hardware flowcontrol '
serial_test('/dev/ttyF1',30,100,'hardware')
print 'ttyF0, test 5, non blocking' 
serial_test('/dev/ttyF0',0,100)
print 'ttyF1, test 5, non blocking'
serial_test('/dev/ttyF1',0,100)
