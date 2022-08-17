#!/usr/bin/env python

import os, sys
import pika
import uuid
import json
from pyedge import PyEdge

user =os.getenv("RABBITMQ_DEFAULT_USER") or "myuser"
password= os.getenv("RABBITMQ_DEFAULT_PASS") or "mypassword"
# helpful for debugging to set another exchange
host = sys.argv[1]
#host = 'localhost'
pe=PyEdge(
    "rpcclient.1",
    host=host,
    user=user,
    password=password
)
print(" [x] Requesting fib(5)")
response=pe.request("demo.1","egal","5")
pe.close()
print(" [.] Got %r" % response)

