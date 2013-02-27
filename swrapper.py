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
import argpass
import random

# ignore this it's just leftover crud, for my reference
# it's going to go away
#def serial_test(device, time_out, bytes_read, flowcontrol = 'none'):
    #"""listens to serial port [device] and prints out N [bytes_read] with timeout [time_out]"""
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


# CLASS DEFINITIONS

class Scale():
    """has serial device, terminator byte,start byte, weight request,weight unit
    A serial device takes the following:
    Device (device) . e.g. /dev/ttyS3, /dev/pts/16
    Speed (speed) in baud. Sefault is 9600
    Byte Size in bits (byte_size). 5,6,7,8 default is 8, 7 is also used in 
    scales and represents true ascii. 8 is the modern standard.
    Device Parity (dev_parity): Can be none, even,odd, mark or space. Typically
    the first 3. A crude form of error checking. Odd means there are always an
    odd number of ones in the byte.
    Stop Bit (stop_bits): 1,2, or 1.5. 1.5 is read as 2 in posix compliant 
    systems. Normally 1. Sent at the end of a character to allow the hardware 
    to dectect the end of the character and resynchronize. 
    Flow Control can be none (default) or hardware or software. Pyserial uses
    xonoxoff=1 for software control rtscts or dsrdtr for the diferent types of 
    hardware control.

    There is also a read read timeout value (timeout) used by pyserial that 
    is passed before the flowcontrol settings. Defaults to none.
    
    The following are specific to the scale class.
    terminator_byte: sent by the scales to mark the end of the message.
        Values include  ASCII carriage return (CR) 0x0E, 
                        ASCII  Record Separator (RS) 0x1E.
    weight_request. Scales operate by receiving single characters as commands.
        This is the character that initiates a weight request.   
    weight_unit , k, g, lb
    """

    def __init__(self, device='', speed = 9600, byte_size = '8', dev_parity = 'none', stop_bits = '1', time_out = None,  flowcontrol = 'None', terminator_byte = '', start_byte = None , weight_request='',weight_unit=''):
        self.device = device
        self.speed = speed
        self.byte_size = byte_size
        self.dev_parity = dev_parity
        self.stop_bits = stop_bits
        self.time_out = time_out
        self.flowcontrol = flowcontrol
        self.terminator_byte = terminator_byte
        self.start_byte = start_byte
        self.weight_request = weight_request
        self.weight_unit = weight_unit
        #    define some dictionaries to address serial constants
        d_bytesize = { '5' : serial.FIVEBITS, 'five' : serial.FIVEBITS,  '6' : serial.SIXBITS,  'six' : serial.SIXBITS, '7' : serial.SEVENBITS, 'seven' : serial.SEVENBITS, '8' : serial.EIGHTBITS, 'eight' : serial.EIGHTBITS}
        d_parity = { 'none' : serial.PARITY_NONE, 'odd' : serial.PARITY_ODD , 'even' : serial.PARITY_EVEN, 'mark' : serial.PARITY_MARK, 'space' : serial.PARITY_SPACE }            
        d_stopbits = { '1' : serial.STOPBITS_ONE, 'one' : serial.STOPBITS_ONE, '2' : serial.STOPBITS_TWO, 'two' : serial.STOPBITS_TWO, '1.5' : serial.STOPBITS_ONE_POINT_FIVE, 'one_point_five' : serial.STOPBITS_ONE_POINT_FIVE }
        # set the values we use to initialize the serial port
        self.port = device
        b_size = str(byte_size)
        self.bytesize = d_bytesize[b_size.lower()]
        self.parity = d_parity[dev_parity.lower()]
        s_bit = str(stop_bits)
        self.stopbits = d_stopbits[s_bit.lower()]
        self.timeout=time_out
        self.baudrate = speed
        # this wont' work as it doesn't get passed on correctly, see commented 
        # example above to h
        try:
            self.serial_port=serial.Serial(self.device, self.baudrate, self.bytesize) #, self.parity) , self.stopbits, self.timeout, self.flowcontrol)
            """Configures a serial port for reading or writing. This is a wrapper to make things friendlier to use, and set some sensible defaults"""
        except serial.SerialException:
            print 'could not open serial device'
        if flowcontrol == 'software':
            self.serial_port.xonxoff = 1
        elif  flowcontrol == 'hardware':
            self.serial_port.rtscts = 1

    def send_weight(self,weight):
        '''sends weight value to pos. N.B. Does not receive weight_request.
        Note this does not attempt to check the weight value is 
        correctly formatted. This should be implented in a wrapper
        function in the relevant class'''
        # none of the defined printers in the pos use a start_byte AFAIK
        if self.start_byte:
            send_string = self.start_byte + weight + self.terminator_byte
        else:
            send_string = weight + self.terminator_byte
        self.serial_port.write(send_string)

    def pos_test(self,dummy_weight):
        '''Tests to ensure we can receive the correct command from the pos,
        and that it correctly receives the weight. Used for debugging.
        You will need to manually initiate a weight request on the pos by
        adding a product (marked scale in properties) to a customers items
        and the checking it has been added correctly. Since we are just testing
        we won't be acutually using any scales but sending a dummy value.
        Note you won't receive an error if you send an incorrectly formatted 
        weight, though one will show in the pos. '''
        try:
            self.serial_port.open()
        except:
            print 'could not open serial port'
        receive = self.serial_port.read(1)
        if receive == self.weight_request:
            self.send_weight(dummy_weight)
            print 'sent ' + dummy_weight
        else:
            print 'expected ' + self.weight_request + '  got: ' + str(ord(receive))
            self.serial_port.close()


class Dialog(Scale):
    """extends Scale, corresponds to built in type Dialog1. This will be used to communicate with the POS. Weight Request 0x05 (ASCII STX: Start of TeXt). Weighs in grams.  """
    def __init__(self, device = ''):
        Scale.__init__(self, device, 4800, '8', 'odd' ,'1', None, 'None', '\x1e', None, '\x05',  'g')


class Samsung(Scale):
    """extends Scale, corresponds to built in type Samsung. This will be used to communicate with the POS. Weight Request $. Weighs in kilos."""
    def __init__(self, device = ''):
        Scale.__init__(self, device, 4800, '8', 'odd' ,'1', None,  'None', '\x0d', None, '$', 'k')

class Dummy(Scale):
    """extends Scale, A dummy external scale for testing purposes. This will return a random weight between 0 & 25 kg (as kg), in 1g increments.. Weight Request $. Weighs in kilos."""
    def __init__(self, device = ''):
        Scale.__init__(self, device, 4800, '8', 'odd' ,'1', None,  'None', '\x0d', None, '$', 'k')


class MagellanSASI(Scale):
    """extends Scale. External scale using SASI-RS232 scale interface. Weighs in kilos or pounds. Weight Request W """
    def __init__(self, device = '', weight_unit=''):
        Scale.__init__(self,device, 9600, '7', 'even', '1', None, 'None', '\x0d', '\x02', 'W', weight_unit)

    def run_echo_test(self):
        self.serial_port.timeout = 10
        self.serial_port.open()
        print 'Beginning echo test...'
        self.serial_port.write("E")                          # enter echo mode
        start_echo = self.serial_port.read(8)                # should be E
        start_echo
        self.serial_port.write("A")
        echo_test1 = self.serial_port.read(4)
        print echo_test1
        self.serial_port.write("Hello World!")
        echo_test2 = self.serial_port.read(16) 
        print echo_test2
        self.serial_port.write("F")                          # exit echo mode
        end_echo = self.serial_port.read(8)
        print end_echo
        self.serial_port.close()

    def run_confidence_test(self):
        self.serial_port.timeout = 10
        self.serial_port.open()
        print 'Beginning confidence test...'
        self.serial_port.write("A")                          # initiate confidence test
        self.serial_port.read(2)                             # read and discard two bytes
        self.serial_port.write("B")                          # get results
        confidence_results = self.serial_port.read(4)        # STX,?,confidence status byte,CR
        confidence_status = bin(ord(confidence_results[3]))
        print 'confidence results: ' + confidence_results + ' confidence status: ' + confidence_status
        results_list = ['eeprom 1', 'eeprom 2', 'ram', 'processor ram', 'rom', 'not used', 'confidence test complete' ,'parity bit']                     # 1 = pass, 0 = fail
        for i in range(0,4):
            if confidence_status[i] == 1:
                print results_list[i] + " test  passed"
            elif confidence_status[i] == 0:
                print results_list[i] + " test  failed"
                flag = 0

            if flag: 
                print "something is wrong, the scale will not work until it is fixed"
        self.serial_port.close()

# FUNCTIONS

def pos_test_samsung(s_port):
    print('starting tests')
    print('opening serial port')
    opos_scale=Samsung(s_port)
    print('start test1')
    opos_scale.pos_test('5')
    print('end test1')
    print('start test2')
    opos_scale.pos_test('5.652')
    print('end test2')
    # generate random float between 0 & 10 and round to 3 decimal places
    rand_weight=round(random.uniform(0,10),3)
    print('start test3')
    opos_scale.pos_test(str(rand_weight))
    print('end test3')

def pos_test_dialog(s_port):
    print('starting tests')
    print('opening serial port')
    opos_scale=Dialog(s_port)
    print('start test1')
    opos_scale.pos_test('500')
    print('end test1')
    # generate random float between 0 & 10 and round to 3 decimal places
    rand_weight=round(random.uniform(0,10),3)
    print('start test2')
    print('end test2')
    opos_scale.pos_test(str(rand_weight))
    print('start test3')
    opos_scale.pos_test(str(rand_weight))
    print('end test3')



# MAIN

if __name__ == "__main__": 
    # pass
    #initialisation
    parser=argparse.ArgumentParser()
    parser.add_argument("--test", help="Run specified test. See README.tests")
    parser.add_argument("--pos", help="specify the serial port the pos is connected to. e.g. /dev/pts/11")
    parser.add_argument("--scale", help="specify the serial port the scale is connected to. e.g. /dev/ttyS3")
    args=parser.parse_args()
    if args.test:
        if args.test == 'samsung':
            pos_test_samsung(args.pos)
        elif args.test == 'dialog':
            pos_test_dialog(args.pos)

