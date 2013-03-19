#!/usr/bin/env python
'''Module that provides functionality to emulate pos scales with 
   serial interfaces'''

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
import random
import ConfigParser
import os
import unittest


# CLASS DEFINITIONS

class Scale():
    """has serial device, terminator byte,start byte, weight request,weight unit
    A serial device takes the following:
    Device (device) . e.g. /dev/ttyS3, /dev/pts/16
    Speed (speed) in baud. Default is 9600
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

    def __init__(self, device='', speed = 9600, byte_size = '8', 
            dev_parity = 'none', stop_bits = '1', time_out = None,  
            flowcontrol = 'None', terminator_byte = '', start_byte = None, 
            weight_request='', weight_unit=''):
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
        self.timeout = time_out
        self.baudrate = speed
        # this wont' work as it doesn't get passed on correctly, see commented 
        # example above to h
        try:
            #Initializes  serial port. 
            self.serial_port = serial.Serial(self.device, self.baudrate, 
                    self.bytesize) 
            #, self.parity) , self.stopbits, self.timeout, self.flowcontrol)
        except serial.SerialException:
            print 'could not open serial device'
        if flowcontrol == 'software':
            self.serial_port.xonxoff = 1
        elif  flowcontrol == 'hardware':
            self.serial_port.rtscts = 1

    def send_weight(self, weight):
        '''sends weight value to pos. N.B. Does not receive weight_request.
        Note this does not attempt to check the weight value is 
        correctly formatted. This should be implented in a wrapper
        function in the relevant class'''
        # none of the defined scales in the pos use a start_byte AFAIK
        if self.start_byte:
            send_string = self.start_byte + weight + self.terminator_byte
        else:
            send_string = weight + self.terminator_byte
        self.serial_port.write(send_string)

    def read_weight(self, signal):
        '''reads (weight)from the serial port on receiving 
        the appropriate signal'''  
        self.signal = signal
        if self.signal == self.weight_request:
            self.time_out = 10
            self.serial_port.write(self.signal)
            read_weight = bytearray()
            while True:
                read_byte = self.serial_port.read(1)
                if read_byte == self.terminator_byte:
                    break
                else:
                    read_weight.append(read_byte)
            if self.start_byte:
                weight = str(ord(read_weight[1:]))
            else:
                weight = str(ord(read_weight))               
            return  weight
        else:
            raise SignalException('expected: ' + self.weight_request 
                    + 'got: ' + str(ord(self.signal)))
    
#    def get_weight(self,signal):
#        self.signal = signal
#        read_weight = read_weight(self.signal)
#        # insert conversion here
#        weight = read_weight
#        return weight

    def pos_test(self, dummy_weight):
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
            print('could not open serial port')
        receive = self.serial_port.read(1)
        if receive == self.weight_request:
            self.send_weight(dummy_weight)
            print( 'sent ' + dummy_weight)
        else:
            print('expected ' + self.weight_request 
            + '  got: ' + str(ord(receive)))
            self.serial_port.close()



class Dialog(Scale):
    """extends Scale, corresponds to built in type Dialog1. 
    This will be used to communicate with the POS. 
    Weight Request 0x05 (ASCII STX: Start of TeXt). Weighs in grams.  """
    def __init__(self, device = ''):
        Scale.__init__(self, device, 4800, '8', 'odd', '1', None, 'None', 
                '\x1e', None, '\x05', 'g')


class Samsung(Scale):
    """extends Scale, corresponds to built in type Samsung. 
    This will be used to communicate with the POS. 
    Weight Request $. Weighs in kilos."""
    def __init__(self, device = ''):
        Scale.__init__(self, device, 4800, '8', 'odd', '1', None, 'None', 
                '\x0d', None, '$', 'k')


class Dummy(Scale):
    """extends Scale, A dummy external scale for testing purposes. 
    This will return a random weight between 0 & 25 kg (as kg), 
    in 1g increments.. Weight Request $. Weighs in kilos."""
    def __init__(self, device = '', weight_unit='k'):
        #Scale.__init__(self, device, 4800, '8', 'odd' ,'1', None,  'None', '\x0d', None, '$', weight_unit)
        self.weight_unit = weight_unit
    def get_weight(self):
        '''returns random weight'''
        if self.weight_unit == 'k':
            rand_weight = round(random.uniform(0, 25), 3)
        if self.weight_unit == 'lb':
            rand_weight = str(round(random.uniform(0, 25), 2)) + '0'
        else:
            raise SignalException('weight unit not defined' )
        print('returning weight: ' + rand_weight)
        return rand_weight


class Toledo(Scale):
    """extends Scale. External scale using Toledo (8213) scale interface.
    Weighs in kilos (grammes) or pounds. Weight Request W 
    Returns: <STX> X1X2X3X4X5 <CR> where X1 to X5 are digits representing
    weight. No decimal point is used so it is sensible to regard kilo as 
    returning grammes."""
    def __init__(self, device = '', speed = '', parity ='', weight_unit=''):
        Scale.__init__(self, device, speed, '7', parity, '1', None, 'None', 
                '\x0d', '\x02', 'W', weight_unit)

    def get_weight(self):
        ''' return  weight read from scale'''
        read_weight = self.read_weight(self.weight_request)
        # The scale always returns a seven byte array(inc start + stop char)
        # kilo returns two digits and three decimal places, 
        # pound mode returns tw and two and  prepends  zeros
        # if we want to weigh in pounds we may have to reverse this
        # since the samsung  expects three decimal points
        # i.e. remove prepending,pad with trailing zero
        # the pos itself is agnostic about weight units though designed for k
        if self.weight_unit == 'lb':
            weight = read_weight[:-2] + '.' +  read_weight[-2:]
        elif self.weight_unit == 'k':
            weight = read_weight[:-3] + '.' +  read_weight[-3:]
        elif self.weight_unit == 'g':
            weight = read_weight
        else: 
            raise SignalException('weight unit not defined')
        return weight


class AcomPC100(Scale):
    """External scale using Toledo scale interface. 
    Weighs in kilos(grammes) or pounds.Weight Request W. 
    Returns: <STX> X1X2X3X4X5 <CR> where X1 to X5 are digits representing
    weight. No decimal point is used so it is sensible to regard kilo as 
    returning grammes."""
    def __init__(self, device = '', weight_unit=''):
        Scale.__init__(self, device, 9600, '7', 'even', '1', None, 'None', 
                '\x0d', '\x02', 'W', weight_unit)

    def get_weight(self):
        ''' return  weight read from scale'''
        read_weight = self.read_weight(self.weight_request)
        # The scale always returns a seven byte array(inc start + stop char)
        # kilo returns two digits and three decimal places, 
        # pound mode returns tw and two and  prepends  zeros
        # if we want to weigh in pounds we may have to reverse this
        # since the samsung  expects three decimal points
        # i.e. remove prepending,pad with trailing zero
        # the pos itself is agnostic about weight units though designed for k
        if self.weight_unit == 'lb':
            weight = read_weight[:-2] + '.' +  read_weight[-2:]
        elif self.weight_unit == 'k':
            weight = read_weight[:-3] + '.' +  read_weight[-3:]
        elif self.weight_unit == 'g':
            weight = read_weight
        else: 
            raise SignalException('weight unit not defined')
        return weight

class SASI(Scale):
    """extends Scale. External scale using SASI-RS232 scale interface. 
    Weighs in kilos or pounds. Weight Request W """
    def __init__(self, device = '', speed = '', parity ='', weight_unit=''):
        Scale.__init__(self, device, speed, '7', parity, '1', None, 'None', 
                '\x0d', '\x02', 'W', weight_unit)

    def get_weight(self):
        ''' return  weight read from scale'''
        read_weight = self.read_weight(self.weight_request)
        # The Magellan always returns a seven byte array(inc start + stop char)
        # kilo returns two digits and three decimal places, 
        # pound mode returns two and two and  appends a zero
        # Note the magellan only works with samsung
        # which seems quite fault tolerant as regards format 
        # the pos itself is agnostic about weight units though designed for k
        if self.weight_unit in [ 'lb', 'k' ]:
            weight = read_weight
        elif self.weight_unit == 'g':
            raise SignalException('scale does not weigh in grammes')
        else : 
            raise SignalException('weight unit not defined')
        return weight


class MagellanSASI(Scale):
    """extends Scale. External scale using SASI-RS232 scale interface. 
    Weighs in kilos or pounds. Weight Request W """
    def __init__(self, device = '', weight_unit=''):
        Scale.__init__(self, device, 9600, '7', 'even', '1', None, 'None', 
                '\x0d', '\x02', 'W', weight_unit)

    def get_weight(self):
        ''' return  weight read from scale'''
        read_weight = self.read_weight(self.weight_request)
        # The Magellan always returns a seven byte array(inc start + stop char)
        # kilo returns two digits and three decimal places, 
        # pound mode returns two and two and  appends a zero
        # Note the magellan only works with samsung
        # which seems quite fault tolerant as regards format 
        # the pos itself is agnostic about weight units though designed for k
        if self.weight_unit in [ 'lb', 'k' ]:
            weight = read_weight
        elif self.weight_unit == 'g':
            raise SignalException('scale does not weigh in grammes')
        else : 
            raise SignalException('weight unit not defined')
        return weight

    def run_echo_test(self):
        '''runs Magellan echo test mode. 
        In this mode the scale will echo whatever is sent to the serial port'''
        self.serial_port.timeout = 10
        self.serial_port.open()
        print 'Beginning echo test...'
        self.serial_port.write("E")                          # enter echo mode
        start_echo = self.serial_port.read(8)                # should be E
        print start_echo
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
        '''Initiates Magellan confidence test. 
        Returns info about state of scale's physical parts e.g. ram/rom ''' 
        self.serial_port.timeout = 10
        self.serial_port.open()
        print 'Beginning confidence test...'
        self.serial_port.write("A")                 # initiate confidence test
        self.serial_port.read(2)                    # read and discard two bytes
        self.serial_port.write("B")                 # get results
        # results: STX,?,confidence status byte,CR
        confidence_results = self.serial_port.read(4)   
        confidence_status = bin(ord(confidence_results[3]))
        print('confidence results: ' + confidence_results 
                + ' confidence status: ' + confidence_status)
        results_list = ['eeprom 1', 'eeprom 2', 'ram', 'processor ram', 'rom', 'not used', 'confidence test complete' ,'parity bit']                     # 1 = pass, 0 = fail
        for i in range(0, 4):
            if confidence_status[i] == 1:
                print results_list[i] + " test  passed"
            elif confidence_status[i] == 0:
                print results_list[i] + " test  failed"
                flag = 0

            if flag: 
                print('something is wrong, the scale will not work until it is fixed')
        self.serial_port.close()

class SignalException(Exception):
    '''used to throw exceptions with user readable error messages'''
    pass

# FUNCTIONS

def pos_test_samsung(s_port):
    '''run tests to make sure samsung scale in pos is working'''
    print('starting tests')
    print('opening serial port')
    opos_scale = Samsung(s_port)
    print('start test1')
    opos_scale.pos_test('5')
    print('end test1')
    print('start test2')
    opos_scale.pos_test('5.652')
    print('end test2')
    print('start test3')
    opos_scale.pos_test('012.34')   # pounds
    print('end test3')
    print('start test4')
    opos_scale.pos_test('56.78')   # pounds
    print('end test4')
    # generate random float between 0 & 10 and round to 3 decimal places
    rand_weight = round(random.uniform(0, 10), 3)
    print('start test5')
    opos_scale.pos_test(str(rand_weight))
    print('end test5')

def pos_test_dialog(s_port):
    '''run tests to make sure dialog scale in pos is working'''
    print('starting tests')
    print('opening serial port')
    opos_scale = Dialog(s_port)
    print('start test1')
    opos_scale.pos_test('500')
    print('end test1')
    # generate random float between 0 & 10000, rounded to whole units
    rand_weight = round(random.uniform(0, 10000))
    print('start test2')
    print('end test2')
    opos_scale.pos_test(str(rand_weight))
    print('start test3')
    opos_scale.pos_test(str(rand_weight))
    print('end test3')

def scale_test_magellan(s_port):
    '''runs tests on external Magellan scale'''
    print('starting tests')
    test_scale = MagellanSASI(s_port)
    test_scale.run_echo_test()
    test_scale.run_confidence_test()
    print('end tests')

def get_config(section):
    '''Reads in configuration file. 
    This provides attributes for the scale setup'''
    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser('~/.swrapper.cfg'), 
        '/etc/swrapper.cfg', 'swrapper.cfg'])
    if config.has_section('pos'):
        pos_values = dict(config.items('pos'))
    if config.has_section('scale'):
        scales_values = dict(config.items('scale'))
    if config.has_option('scale', 'type'):
        defined_scale = config.get('scale', 'type')
        if config.has_section(defined_scale):
            scale_definition = dict(config.items(defined_scale))
    if section == 'pos':
        if pos_values:
            return pos_values
    elif section == 'scale':
        if scales_values:
            return scales_values
    elif section == 'scale_definition':
        if scale_definition:
            return scale_definition

# Unit Tests

class MyUnitTest(unittest.TestCase):
    '''unit tests for non class functions'''
    def test_config_pos(self):
        '''reads config file (unedited) for pos scale type'''
        pos_config = get_config('pos')
        self.assertEqual(pos_config['type'], 'samsung')

    def test_config_scale(self):
        '''reads config file (unedited) for external scale type'''
        scale_config = get_config('scale')
        self.assertEqual(scale_config['type'], 'example')

    def test_defined_scale(self):
        '''reads config file (unedited) for example scale definitions'''
        defined_scale = get_config('scale_definition')
        self.assertEqual(defined_scale['speed'], '9600')

if __name__ == "__main__":
    unittest.main()
