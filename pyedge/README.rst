*****
pyEdge
*****


PyEdge is a library for a simple message exchange using the rabbitMQ protocol between a swarm of Diagnostic UNIts (the Duni's) and a
central controlling instance

The architecture is given by design, and the pyEdge interface is made to hide all the internals from the clients 


::

 wget  https://github.com/stko/pyedge/archive/master.zip -O tmpfile \
 && unzip tmpfile \
 && cd pyedge 

::

 sudo su
 python setup.py install
 exit
 

