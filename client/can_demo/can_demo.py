import os
from pyedge import PyEdge
import isotp
import can
import time


def can_message(isotp_request):
	s = isotp.socket()
	s2 = isotp.socket()
	# Configuring the sockets.
	s.set_fc_opts(stmin=5, bs=10)
	# s.set_general_opts(...)
	# s.set_ll_opts(...)
	s.bind("vxcan0", isotp.Address(
		rxid=isotp_request["rxid"], txid=isotp_request["txid"]))
	s2.bind("vxcan0", isotp.Address(
		rxid=isotp_request["txid"], txid=isotp_request["rxid"]))
	s2.send(b"Hello, this is a long payload sent in small chunks of 8 bytes.")
	answ = s.recv()
	s.close()
	s2.close()
	if answ:
		return {"dtl": len(answ), "data": answ.decode()}
	else:
		return {"dtl": 0}

''' besser nicht direkt beim Start auf den Bus zugreifen, der ist nämlich vielleicht noch gar nicht virtualisert
bustype = 'socketcan'
channel = 'vcan0'

def producer(id):
    """:param id: Spam the bus with messages including the data id."""
    bus = can.Bus(channel=channel, interface=bustype)
    for i in range(10):
        msg = can.Message(arbitration_id=0xc0ffee, data=[id, i, 0, 1, 3, 1, 4, 1], is_extended_id=False)
        bus.send(msg)

    time.sleep(1)

producer(10)
'''


module_name = os.getenv("MODULE_NAME") or 'can_demo'
module_index = os.getenv("MODULE_INDEX") or "1"
module_queue = '.'.join([module_name, module_index])
duni_id = os.getenv("DUNI_ID") or "4711"
user = os.getenv("RABBITMQ_DEFAULT_USER") or "myuser"
password = os.getenv("RABBITMQ_DEFAULT_PASS") or "mypassword"
# helpful for debugging to set another exchange
host = os.getenv("DUNI_HOST") or 'exchange'
pe = PyEdge(
    module_queue,
    host=host,
    user=user,
    password=password,
	purge=True
)
pe.add_handler("", can_message)

# message loop
pe.runforever()
