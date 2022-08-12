#!/usr/bin/env python
import os
import sys
import pika
import time

try:
    from pyedge import PyEdge
except:
    ScriptPath = os.path.realpath(os.path.join(
        os.path.dirname(__file__), "../.."))
    # Add the directory containing your module to the Python path (wants absolute paths)
    sys.path.append(os.path.abspath(ScriptPath))
    from pyedge import PyEdge


def fib(n):
    n=int(n)
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


module_name = os.getenv("MODULE_NAME") or 'demo'
module_index = os.getenv("MODULE_INDEX") or "1"
module_queue = '.'.join([module_name, module_index])
duni_id = os.getenv("DUNI_ID") or "4711"
user =os.getenv("RABBITMQ_DEFAULT_USER") or "myuser"
password= os.getenv("RABBITMQ_DEFAULT_PASS") or "mypassword"
# helpful for debugging to set another exchange
host = os.getenv("DUNI_HOST") or 'exchange'
pe = PyEdge(
    module_queue,
    host="localhost",
    user=user,
    password=password,
)
pe.add_handler("", fib)
pe.runforever()
