#!/usr/bin/env python


#    Copyright Paul Munday 2013

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



import serial

#def serial_test(device, time_out, bytes_read, flowcontrol = 'none'):
    #'''listens to serial port [device] and prints out N [bytes_read] with timeout [time_out]'''
    #try:
        #ser = serial.Serial(device, 4800, parity=serial.PARITY_ODD, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, timeout=time_out)
        #if flowcontrol == 'software':
            #ser.xonxoff = 1
        #elif  flowcontrol == 'hardware':
            #ser.rtscts = 1
        #buffer_input = ser.read(bytes_read)
        #ser.close()
        #print 'received:' + buffer_input
        #if len(buffer_input) == 0:
            #print 'there was no input'
        #else:
            #print 'Input was:' + buffer_input
    #except serial.SerialException:
        #print 'could not open serial device'
        #pass

def serial_conf(device,speed = 9600, dev_parity = 'none' , byte_size = '8', stop_bitsa = '1', time_out = 'None',  flowcontrol = 'None'):
    '''Configures a serial port for reading or writing. This is just a wrapper to make things friendlier to use, and set some sensible defaults'''
    
    #    define some dictionaries to address serial constants
    d_parity = { 'none' : 'serial.PARITY_NONE', 'odd' : 'serial.PARITY_ODD', 'even' : 'serial.PARITY_EVEN', 'mark' : 'serial.PARITY_MARK', 'space' : 'serial.PARITY_SPACE' } 
   d_bytesize = { '5' : 'serial.FIVEBITS', 'five' : 'FIVEBITS',  '6' : 'SIXBITS',  'six' : 'SIXBITS', '7' : 'SEVENBITS', 'seven' : 'SEVENBITS', '8' : 'EIGHTBITS', 'eight' : 'EIGHTBITS'}
   d_stopbits = { '1' : 'STOPBITS_ONE', 'one' : 'STOPBITS_', '2' : 'STOPBIT_TWO', 'two' : 'STOPBITS_TWO', '1.5' : 'STOPBITS_ONE_PONT_FIVE', 'one_point_five' : 'STOPBITS_ONE_PONT_FIVE' }
    try:
        ser = serial.Serial()
        ser.port = device
        try:
        ser.parity = d_parity[dev_parity.lower()]
        except serial.ValueError:
            print 'parity is invalid'
            ser.parity = serial.PARITY_NONE
            pass
        try:
            b_size = str(byte_size)
            ser.bytesize = d_bytesize[b_size.lower()]
        except serial.ValueError:
            print 'invalid bytesize'
            ser.bytesize = EIGHTBITS
            pass
        try s_bit = str(stop_bits)
            ser.stopbits = d_stopbits[s_bit.lower()]
        except  serial.ValueError:
            ser.stopbits = STOPBITS_ONE
            pass
        try:
            ser.timeout=time_out
        except serial.ValueError:
            print 'timeout out of range'
            ser.timeout = 'None'
            pass
        try:
            ser.baudrate = speed
        except serial.ValueError:
            print 'baudrate out of range'
            speed = 9600
            pass
        if flowcontrol == 'software':
            ser.xonxoff = 1
        elif  flowcontrol == 'hardware':
            ser.rtscts = 1
    except serial.SerialException:
        print 'could not open serial device'
        pass
