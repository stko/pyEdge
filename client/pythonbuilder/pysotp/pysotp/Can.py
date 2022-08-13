#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from ctypes import *

import binascii

OK = 0
ERR = -1
ERR_TIMEOUT = -2

required_dll = os.path.join(os.path.dirname(__file__), 'libcanwrap.so')
dll = cdll.LoadLibrary(required_dll)


def convert_name(name):
	return name.lower().split('.')[-1].replace(' ', '_')


def can_isotp_start(buffer_size=20):

	# initialize
	ret = dll.reserveBuffer(buffer_size)
	if ret < 0:
		raise Exception('Error on initialization')

def can_raw_start(canInterface='can0'):

	# initialize

	ret = dll.raw_can_init(canInterface, len(canInterface))
	if ret < 0:
		raise Exception('Error on initialization')


def can_stop():
	dll.iso_tp_stop()
	dll.raw_can_stop()


class IsoTp:

	def __init__(self, can_bus, module):
		try:
			tx = module['tx']
			rx = module['rx']
		except KeyError:
			raise Exception('Invalid iso-tp module')
		ret = dll.iso_tp_map_channel(can_bus, tx, rx)
		if ret < 0:
			raise Exception('Error on mapping module: {}'.format(ret))
		self.module=module
		self.ch_id = ret

	def iso_tp_flush_rx(self):
		ret = dll.iso_tp_flush_rx(self.ch_id)
		if ret < 0:
			raise Exception('Error flushing: {}'.format(ret))

	def iso_tp_send(self, data):
		if not isinstance(data, bytearray):
			data = bytearray.fromhex(data)
		ret = dll.iso_tp_send(self.ch_id, str(data), len(data))
		if ret < 0:
			raise Exception('Error sending: {}'.format(ret))

	def iso_tp_send_and_receive(
		self,
		data,
		timeout=200,
		):
		self.iso_tp_send( data)
		rec_data = create_string_buffer(4095)
		rec_len = c_int()
		ret = dll.iso_tp_receive(self.ch_id, rec_data, byref(rec_len),
								 int(timeout))
		if ret == ERR:
			raise Exception('Error receiving')
		elif ret == ERR_TIMEOUT:
			raise Exception('Timeout expired without receiving data')
		rec_data = bytearray(rec_data.raw[:rec_len.value])
		return rec_data


class RawCan:
	def __init__(self):
		self.ch_ids = {}

	def raw_can_flush_rx(self, module):
		try:
			ch_id = module['rawsocket']
		except KeyError:
			raise Exception('Unmapped module')
		ret = dll.raw_can_flush_rx(ch_id)
		if ret < 0:
			raise Exception('Error flushing: {}'.format(ret))

	def raw_can_map_channel(self, module):
		try:
			can_id = module['tx']
		except KeyError:
			raise Exception('Invalid raw can module')
		ret = dll.raw_can_map_channel(can_id)
		if ret < 0:
			raise Exception('Error on mapping module: {}'.format(ret))
		module['rawsocket'] = ret

	def raw_can_send(self, module, data):
		if not isinstance(data, bytearray):
			data = bytearray.fromhex(data)
		try:
			ch_id = module['rawsocket']
		except KeyError:
			raise Exception('Unmapped module')
		ret = dll.raw_can_send(ch_id, str(data), len(data))
		if ret < 0:
			raise Exception('Error sending: {}'.format(ret))

	def raw_can_receive_and_check(
		self,
		module,
		data,
		timeout,
		):
		ch_id = module['rawsocket']
		rec_data = create_string_buffer(8)
		rec_len = c_int()
		ret = dll.raw_can_receive(ch_id, rec_data, byref(rec_len),
								  int(timeout))
		if ret == ERR:
			raise Exception('Error receiving')
		elif ret == ERR_TIMEOUT:
			raise Exception('Timeout expired without receiving data')
		rec_data = str(bytearray(rec_data.raw[:rec_len.value]))
		exp_data = str(bytearray.fromhex(data))
		if rec_data != exp_data:
			raise Exception('''
Expected data: {}
Received data: {}'''.format(exp_data,
							rec_data))
		else:
			return rec_data
