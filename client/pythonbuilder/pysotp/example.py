#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
#-----------------for development only: Load the can module from the local subfolder
import os, sys, inspect

# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)


# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"pysotp")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)
from Can import *	
#---------------------------	
'''

from pysotp import *
from modules import modules

import time

import binascii




try:
	from FordStuff import key_from_seed
	import FordStuff

except ImportError:
	# dummy declarations, in case FordStuff is not installed
	def key_from_seed(a,b,c): 
		return False
	
	class FordStuff: 
		secret_keys = {
		}

class SampleModule(IsoTp):	
	def send(self,request):
		try:
			answer=self.iso_tp_send_and_receive( request,500)
			print(": {0} -> {1}".format(request,binascii.hexlify(answer)))
			return answer
		except Exception as inst:
			print type(inst)     # the exception instance
			print inst.args      # arguments stored in .args
			print inst           # __str__ allows args to be printed directly		print(": {0} -> -".format(request))
			return bytearray()
		
		
	def accessMode(self, opMode, seclevel):
		# first of all switch into the requested session mode
		udsBuffer=self.send("10 {:02X}".format(opMode))
		if len(udsBuffer)>0:
			if udsBuffer[0]!=0x50:
				return -1
		else:
			return -2
		if seclevel == 0 :
			return 0 # just changed the mode, nothing more to do
		udsBuffer=self.send("27 {:02X}".format(seclevel))
		if len(udsBuffer)>0:
			if udsBuffer[0]==0x67:
				if udsBuffer[1] == seclevel:
					if udsBuffer[ 2 ] == 0  and  udsBuffer[ 3 ] == 0  and  udsBuffer[ 4 ] == 0:
					# access already granted previously..
						return seclevel
					else:
						# to let FordStuff act correcty, we need to put the code to use first into the right place before call the seed calculation
						if "seccodes" in self.module and  seclevel in self.module["seccodes"]:
							FordStuff.secret_keys [self.module["tx"]]=self.module["seccodes"][seclevel]
						else:
							FordStuff.secret_keys [self.module["tx"]]="00 00 00 00 00"
						seed=key_from_seed(self.module["tx"],"{:02X} {:02X} {:02X}".format( udsBuffer[ 2 ] , udsBuffer[ 3 ] , udsBuffer[ 4 ] ),1)
						udsBuffer=self.send("27 {:02X} {:02X} {:02X} {:02X}".format( seclevel + 1 , seed[ 0 ] , seed[ 1 ] , seed[ 2 ] ) )
						if len(udsBuffer)>0:
							if udsBuffer[ 0 ] == 0x67 and udsBuffer[ 1 ] == seclevel + 1 :
								return seclevel
							else:
								return -4
						else:
							return -5
				else:
					return -6
			else:
				print ("Error response: {:02X} {:02X}".format(udsBuffer[0],udsBuffer[2]))
				return -7
		else:
			return -8


	def simplesend(self,prefix,mask, byteseq):
		answer=self.send( prefix+" "+mask+" "+byteseq)
		print(": {0} -> {1}".format(request,binascii.hexlify(answer)))
		time.sleep( 0.3 )
		#self.iso_tp_send_and_receive(prefix+" "+mask+" 00 00 00 00",500)


can_isotp_start()
#raw = RawCan()
#raw.raw_can_map_channel('my_channel_1')
#raw.raw_can_send('my_channel_1', '01 23 XX 45')
myModule = SampleModule("can0",modules["ECU"])



udsBuffer=myModule.send('19 00') # send a hex string
udsBuffer=myModule.send(bytearray.fromhex('22 71 51')) # send a byte array
if len(udsBuffer)>0:
	if myModule.accessMode( 3, 3 )>-1:
		mask="FF FF FF FF" # mask for all outputs
		while True:
		  prefix="2F A4 61 03" 
		  myModule.simplesend(prefix,mask,"02 00 00 00")



