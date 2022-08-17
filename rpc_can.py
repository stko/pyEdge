#!/usr/bin/env python

import os, sys
from pyedge import PyEdge

user =os.getenv("RABBITMQ_DEFAULT_USER") or "myuser"
password= os.getenv("RABBITMQ_DEFAULT_PASS") or "mypassword"
# helpful for debugging to set another exchange
host = sys.argv[1]
#host = 'localhost'
pe=PyEdge(
    "rpccan.1",
    host=host,
    user=user,
    password=password
)
print(" [x] Requesting can")
response=pe.request("can_demo.1","egal",{"rxid": 0x123, "txid":0x123+8, "data":bytearray.fromhex('22 71 51').decode()})
print(" [.] Got %r" % response)

