*****
Intro
*****


This a modified version of the original pysotp from `OTAKeys <https://github.com/OTAkeys/pysotp>`_. While the original software is made to include isotp into the Robottest Framework, this version is more tailored to allow communication with electronic modules inside vehicles as part of the `OOBD <https://oobd.org>`_ tool sets. For that several functions and structures have been modified.

The main differences to the original are:

* all robotframework references and logging functions removed
* the channels.py configuration concept is replaced against module.py (see module_template.py), which references the module tx/rx and optional security codes just by the symbolic module name
* hard coded limit of channels replaced against initialisation during startup
* supports multiple can devices instead of only one
* each channel is now it's own object, representing a single module
* datalist removed; internal can data variables all set to byte array type to avoid several string castings
* basic support Ford security access handling by using external, not supported python module as optional add-on  

Setup
=====

can-isotp Installation
----------------------


As the can-isotp kernel module seems not to be available as debian package yet, we need to compile the module by ourself:

1. Download repository

      ``git clone https://github.com/hartkopp/can-isotp.git``

2. Build ISO-TP kernel module

   Ensure dependencies are installed.  For Debian (or Ubuntu):

      ``sudo apt-get install build-essential linux-headers-$(uname -r)``

   To build:

   On Ubuntu 16.04, you might need to tweak the KERNEL_VERSION directive in isotp.c:1112 (just check the error message, in case)

      ``make``

   To install (optional, but recommended):

      ``sudo make modules_install``


3. When the PF_CAN core module is loaded ('modprobe can') the ISO-TP module
   can be loaded into the kernel with

       ``insmod ./net/can/can-isotp.ko``

   When the can-isotp.ko module has been installed into the Linux Kernels
   modules directory (e.g. with 'make modules_install') the module should
   load automatically when opening a CAN_ISOTP socket.



Pysotp
======

A Python library for raw CAN and ISO-TP over SocketCAN
------------------------------------------------------


Originally this library was used as a CAN library for robot framework, but it can also be used as a general ISO-TP and raw CAN library for Python.

Usage:

make sure clang is installed (maybe somebody whould like to change this to the smaller gcc?)

``sudo apt-get install clang``


In opposite to the original OTAKeys pysotp version, this one is modified to work with the standard python setuptools. To install, download this repository and run the python setup by

::

 wget  https://github.com/stko/pysotp/archive/master.zip -O tmpfile \
 && unzip tmpfile \
 && cd pysotp 

::

 sudo su
 python setup.py install
 exit
 



Set the CAN interface up:

::
 sudo ip link set can0 type can bitrate 125000 triple-sampling on
 sudo ip link set can0 up

The accompanied udev rule is specific for PCAN-USB CAN interfaces, but can easily be modified for different CAN interfaces.

Copy the udev rule and corresponding script to the right directories:
::

 cp 90-can-interface.rules /etc/udev/rules.d/
 cp setup_can_iface.sh /usr/local/bin/


Now setup_can_iface.sh script is run by udev when a can interface is plugged in. This script makes sure the correct drivers are loaded and the interface is set to up.

CAVEAT: When a new kernel version is installed, you might have to copy the the can-isotp.ko kernel module again to the modules directory.


FordStuff
---------
**DISCLAIMER: The Use of the Ford Security Access library might violate laws or regulations in some countries. Install and use that library only when being aware about any potential effects. For further details see also LICENCE**

The FordStuff library is the result of some reverse engineering activities of american scientists. It allows to activate advanced functions on some Ford electronic modules. In case of questions please contact the authors directly, we do not provide any support or further details on that.

By following the instruction below how to install you agree to the a.m. disclaimer and the LICENSE terms.

To install the FordStuff library, download FordStuff.py from github.com/Self-Driving-Vehicle/CANBUS-Hack/raw/master/code/ecomcat_api/FordStuff.py and place it in your local directory