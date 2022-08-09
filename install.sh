
#####  Installs the pyEdge Docker setup on Unix, exspecially made for Raspi SoCs
# To install piInfoDisplay, get a virgin RaspiOS lite image from raspberry.org
# tested on raspian stretch
#  boot the virgin raspian image, login
#  do 'export DEBUG=YES' first, if the finished image shall not become read-only. This is good for debugging, but bad for daily use..
#
# start the install script with
#    bash <(curl -s https://raw.githubusercontent.com/stko/piInfoDisplay/master/install.sh)
# and spent some hours with your friends or family. When you are back,
# the installation should be done

PROGNAME=pyEdge

echo "The $PROGNAME Installer starts"
cd
HOME=$(pwd)
sudo apt-get update --assume-yes
sudo apt-get install --assume-yes \
joe \
git \
usbmount \
docker.io docker-compose 

if [[DEBUG -eq YES]] ; then
	git clone https://github.com/stko/$PROGNAME
else
	wget  https://github.com/stko/$PROGNAME/archive/master.zip -O $PROGNAME.zip && unzip $PROGNAME.zip
	mv $PROGNAME-master $PROGNAME
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
mqhost =${mqhost:-rabbitMQ}
read -p "Enter the rabbitMQ port [5672]: " mqport
mqport =${mqport:-5672}
read -p "Enter the rabbitMQ user name  [myuser]: " mquser
mquser =${mquser:-myuser}
read -p "Enter the rabbitMQ password  [mypassword]: " mqpassword
mqpassword =${mqpassword:-mypassword}



# create .venv
cd  $PROGNANE
python3 -m venv .venv
source .venv/bin/activate
python -m pip install  -r requirements.txt

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
ExecStart=$HOME/$PROGNAME/$PROGNAME.sh --host $mqhost --port $mqport --user $mquser --password $mqpassword
Restart=on-failure

[Install]
WantedBy=default.target

EOF


# sudo systemctl enable $PROGNAME


cat << 'EOF'
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

