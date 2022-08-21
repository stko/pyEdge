#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )



#####  Installs the pyEdge Docker setup on Unix, exspecially made for Raspi SoCs
# To install piInfoDisplay, get a virgin RaspiOS lite image from raspberry.org
# tested on raspian stretch
#  boot the virgin raspian image, login
#  do 'export DEBUG=YES' first, if the finished image shall not become read-only. This is good for debugging, but bad for daily use..
#
# start the install script with
#    curl -s https://raw.githubusercontent.com/stko/pyEdge/master/install.sh -o install.sh && bash install.sh

PROGNAME=pyEdge

echo "The $PROGNAME Installer starts"
sudo apt-get update --assume-yes
sudo apt-get install --assume-yes \
joe \
git \
python3-venv \
docker.io docker-compose 


# add user to docker user group - need to re-login to activate
sudo usermod -aG docker $USER

# try to identify architecture
ARCH=$( uname -m )

# add docker compose for docker version < 2.0
# create the docker plugins directory if it doesn't exist yet
mkdir -p ~/.docker/cli-plugins
# download the CLI into the plugins directory
if [ $ARCH = "x86_64" ] ; then
	curl -sSL https://github.com/docker/compose/releases/download/v2.10.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
else
	curl -sSL https://github.com/docker/compose/releases/download/v2.10.0/docker-compose-linux-armv7 -o ~/.docker/cli-plugins/docker-compose
fi
# make the CLI executable
chmod +x ~/.docker/cli-plugins/docker-compose

# and do the same because the pyEdge- Service runs as root, so also root need this extension
# create the docker plugins directory if it doesn't exist yet
sudo mkdir -p /root/.docker/cli-plugins
sudo cp ~/.docker/cli-plugins/docker-compose /root/.docker/cli-plugins


#add docker buildx support
# create the docker plugins directory if it doesn't exist yet
mkdir -p ~/.docker/cli-plugins
# download the CLI into the plugins directory
if [ $ARCH = "x86_64" ] ; then
	curl -sSL https://github.com/docker/buildx/releases/download/v0.9.1/buildx-v0.9.1.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
else
	curl -sSL https://github.com/docker/buildx/releases/download/v0.9.1/buildx-v0.9.1.linux-arm-v7 -o ~/.docker/cli-plugins/docker-buildx
fi

# make the CLI executable
chmod +x ~/.docker/cli-plugins/docker-buildx

# and do the same because the pyEdge- Service runs as root, so also root need this extension
# create the docker plugins directory if it doesn't exist yet
sudo mkdir -p /root/.docker/cli-plugins
sudo cp ~/.docker/cli-plugins/docker-buildx /root/.docker/cli-plugins



# we install usbmount seperately as this causes an error msgs on unbuntu server test env
sudo apt-get install --assume-yes \
usbmount 

if [[DEBUG -eq YES]] ; then
	git clone https://github.com/stko/$PROGNAME.git
else
	wget  https://github.com/stko/$PROGNAME/archive/refs/heads/main.zip -O $PROGNAME.zip && unzip $PROGNAME.zip
	mv $PROGNAME-main $PROGNAME
fi
# uncomment in case of special config files
# sudo mkdir /etc/$PROGNAME
# sudo cp $PROGNAME/scripts/sample_* /etc/$PROGNAME/
# sudo rename 's/sample_//' /etc/$PROGNAME/sample*


# add the usb-drive to the mountlist
cat << 'MOUNT' | sudo tee -a /etc/fstab
/dev/sda1       /media/usb0     vfat    ro,defaults,nofail,x-systemd.device-timeout=1   0       0
MOUNT

# get parameters
read -p "Enter the rabbitMQ Host or ip address [rabbitMQ]: " mqhost
mqhost="${mqhost:=rabbitMQ}"
read -p "Enter the rabbitMQ port [5672]: " mqport
mqport="${mqport:=5672}"
read -p "Enter the rabbitMQ user name  [myuser]: " mquser
mquser="${mquser:=myuser}"
read -p "Enter the rabbitMQ password  [mypassword]: " mqpassword
mqpassword="${mqpassword:=mypassword}"



# create .venv
echo SCRIPT_DIR $SCRIPT_DIR
cd $SCRIPT_DIR
cd  $PROGNAME
cd client

python3 -m venv .venv
source .venv/bin/activate
pwd
ls -a
python -m pip install  -r requirements.txt


# set the executable flag
chmod a+x *.sh

# setting up the systemd services
# very helpful source : http://patrakov.blogspot.de/2011/01/writing-systemd-service-files.html

# EOF is NOT quoted ('') to allow variable substitution in the HERE document
cat << EOF | sudo tee  /etc/systemd/system/$PROGNAME.service
[Unit]
Description=$PROGNAME Main Server
After=network.target
After=docker.service
BindsTo=docker.service
ReloadPropagatedFrom=docker.service

[Service]
WorkingDirectory=$SCRIPT_DIR/$PROGNAME/client
ExecStart=$SCRIPT_DIR/$PROGNAME/client/.venv/bin/python pyedge_bootstrap.py --host $mqhost --port $mqport --user $mquser --password $mqpassword
Restart=on-failure

[Install]
WantedBy=default.target

EOF


# sudo systemctl enable $PROGNAME


cat << EOF
Installation finished

SSH is enabled and the default password for the 'pi' user has not been changed.
This is a security risk - please login as the 'pi' user and type 'passwd' to set a new password."

Also this is the best chance now if you want to do some own modifications,
as with the next reboot the image will be write protected

if done, end this session with
 
     sudo halt

and your $PROGNAME all-in-one is ready to use

have fun :-)

the $PROGNAME team
EOF

sync
sync
sync

