
##### To install pysotp on a embedded device, open a terminal window there and start the installation
#  by downloading and run this installation script like
#  bash <(curl -s https://github.com/stko/pysotp/raw/master/install.sh)
#
#  See also the documentation on https://github.com/stko/pysotp
#
# This script is tailored for a Raspberry Pi raspbian OS
#
#

echo "The pysotp Installer starts"
cd

mkdir -p insttemp bin/oobd/oobdd bin/oobd/fw
cd insttemp
sudo apt-get update --assume-yes
sudo apt-get install --assume-yes \
build-essential \
libsocketcan2 \
libsocketcan-dev \
linux-headers-$(uname -r) \
can-utils 


if [ ! -f can-isotp-master.zip ]; then
	wget  https://github.com/hartkopp/can-isotp/archive/master.zip -O can-isotp-master.zip && unzip can-isotp-master.zip
fi

if [ ! -f pysotp-master.zip ]; then
	wget  https://github.com/stko/pysotp/archive/master.zip -O pysotp-master.zip && unzip pysotp-master.zip
fi

cd can-isotp-master \
&& make \
&& cd
#&& make \
#&& sudo make modules_install
#&& cd ~/insttemp \
#&& rm -r oobd-development


############### raspbian kernel sources #############
### this part is not working yet, so it's commented out
# sudo wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source  -O /usr/bin/rpi-source && sudo chmod +x /usr/bin/rpi-source && /usr/bin/rpi-source -q --tag-update
# rpi-source --skip-gcc


cd ~/bin/oobd/oobdd && unzip ~/oobdd.zip
chmod a+x /home/pi/initoobd.sh



echo "Installation finished"


