import threading  
import time
import struct
import minimalmodbus as mb

c = mb.Instrument('COM10', 1)
c.serial.baudrate = 115200
print c

def get_R( addr ) :
    temp = 0
    addr_len = len( addr )
    #print R_len
    if ( addr_len > 4 ) :
        print "Error address of relay, too long"
        return None
    else :
        #s_head = R[0]
        #print s_head
        s_dec = addr[:(addr_len-1)]
        #print s_dec
        s_hex = addr[addr_len-1]
        #print s_hex
        if ( s_dec == "" ) :
            n_dec = 0
        else:
            n_dec = int(s_dec)
            #print n_dec
        #end if-else
        n_hex = int( s_hex, 16 )
        #print n_hex
        
        #address transform 
        maddr = ((n_dec * 16) + n_hex) + 2048
        #print maddr
        while True:
            try:
                temp = c.read_bit( maddr, 1 ) #1:read R from fp-x, 2:read X from fp-x
            except:
                pass
            else:
                break
        #end while
    #end if-else
    return temp
#end def get_R

def set_R( addr, state ):
    addr_len = len( addr )
    #print R_len
    if ( addr_len > 4 ) :
        print "Error address of relay, too long"
        return None
    else :
        s_dec = addr[0:(addr_len-1)]
        s_hex = addr[addr_len-1]
        if ( s_dec == "" ) :
            n_dec = 0
        else:
            n_dec = int(s_dec)
            #print n_dec
        #end if-else
        n_hex = int( s_hex, 16 )
        #print n_hex
        
        #address transform
        maddr = ((n_dec * 16) + n_hex) + 2048
        #print maddr
        while True:
            try:
                if state :
                    c.write_bit(maddr,1)
                else :
                    c.write_bit(maddr,0)
                #end if-else
            except:
                pass
            else:
                break
        #end while
    #end if-else
    return
#end def set_R

# n = 0:32764, represent DT0~DT32764
# type = "int", "long", "float"
def get_DT( addr, mytype ):
    if ( addr < 0 ) or ( addr > 32764 ) :
        print "Address of DT is out of range."
        return None
    #end if
    myint, mylong = 0, 0
    myfloat = 0.0
    temp, temp1 = 0, 0
    a0, a1 = "", ""
    if mytype == "int" :
        while True:
            try:
                myint = c.read_register( addr )
            except:
                pass
            else:
                break
        #end while
        return myint
    elif mytype == "long" :
        while True:
            try:
                #mylong = c.read_long(n)
                temp = c.read_registers( addr, 2 )
            except:
                pass
            else:
                a0 = struct.pack('H', temp[0])
                a1 = a0 + struct.pack('H', temp[1])
                temp1 = struct.unpack('l', a1)
                mylong =  temp1[0]
                #print temp1
                break
        #end while
        #print "not ready yet"
        return mylong
    elif mytype == "float" :
        while True:
            try:
                temp = c.read_registers( addr, 2 )
            except:
                pass
            else:
                a0 = struct.pack('H', temp[0])
                a1 = a0 + struct.pack('H', temp[1])
                temp1 = struct.unpack('f', a1)
                myfloat = temp1[0]
                break
        #end while
        return myfloat
    else :
        print "Wrong type found, please do re-check"
        return None
    #end if-else
#end get_DT

def get_DTs(addr, n):
    get_values = [0]
    retry = 0
    while True:
        try:
            get_values = c.read_registers( addr, n )
            retry = retry + 1
        except:
            if retry > 5 :
                break
            else:
                pass
            #end if-else
        else:
            break
    #end While
    return get_values
#end get_DTs

# addr = 0:32764, represent DT0~DT32764
# type = "int", "long", "float"
def set_DT( addr, myval ):
    if ( addr < 0 ) or ( addr > 32764 ) :
        print "Address of DT is out of range."
        return None
    #end if
    retry = 0
    temp, temp1 = 0, 0
    word, word1 = 0, 0
    aa, a0, a1 = "", "", ""
    if type(myval) is int :
        if (myval > 65535) :
            print str(myval) + " is long"
            return
        #end if
        retry = 0
        while True:
            try:    
                c.write_register( addr, myval )
                retry = retry + 1
            except:
                if retry > 5 :
                    break
                else:
                    pass
                #end if-else
            else:
                break
        #end while
        #return None
    elif type(myval) is long :
        retry = 0
        word = (myval & 0x0000FFFF) & 0xFFFF #lo byte
        word1 = (myval >> 16) & 0xFFFF #hi byte
        #print hex(word) + ":" + str(word)
        #print hex(word1) + ":" + str(word1)
        a0 = struct.pack('H', word)
        #print a0
        a1 = struct.pack('H', word1) + a0
        #print a1
        temp1 = struct.unpack('l', a1)
        #print temp1
        while True:
            try:
                c.write_long( addr, temp1[0], True )
                retry = retry + 1
                #print retry
            except:
                if retry > 5 :
                    break
                else:
                    pass
                #end if-else
            else:
                break
        #end while
        #print "not ready yet"
        #return temp1[0]
    elif type(myval) is float :
        retry = 0
        aa = hex(struct.unpack('!I', struct.pack('!f', myval))[0])[2:].zfill(8)
        word = int(aa[4:], 16) #lo byte
        word1 = int(aa[:4], 16) #hi byte
        #print word
        #print word1
        a0 = struct.pack('H', word)
        a1 = struct.pack('H', word1) + a0
        temp1 = struct.unpack('f', a1)
        while True:
            try:
                c.write_float( addr, temp1[0] )
                retry = retry + 1
            except:
                if retry > 5 :
                    break
                else:
                    pass
                #end if-else
            else:
                break
        #end while
        #print "not ready yet"
        #return temp1[0]
    else :
        print "Wrong type found(int, long, float ONLY), please do re-check"
        return None
    #end if-else
#end set_DT

def set_DTs( addr, myvals ):
    retry = 0
    while True:
        try:
            c.write_registers( addr, myvals )
            retry = retry + 1
        except:
            if retry > 5 :
                break
            else:
                pass
            #end if-else
        else:
            break
    #end While
#end set_DTs

''' USAGE '''
#print "read function test..."
#print "read DT400 as 32-bits int(long): " + str(read_DT(400,"long"))
#print "read DT1 as 16-bits int: " + str(read_DT(1,"int"))
#print "read DT140 as 32-bit float: " + str(read_DT(140,"float"))
#print "write function test..."
print "R101 set ON..."
set_R("101",1)
set_R("1101",1)
print "R101 is: " + str(get_R("101"))
set_R("101",0)
set_R("1101",0)
print "set DT140 to 12.3..."
set_DT(140, 12.3)
print "DT140 is: " + str(get_DT(140, "float"))
print "DT1 set to 81"
set_DT(1, 81)
print "DT1 is: " + str(get_DT(1, "int"))
print "DT400 set to 1600899904"
set_DT(400, 1600899904l)
print "DT400 is: " + str(get_DT(400, "long"))
