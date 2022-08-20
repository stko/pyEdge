
# https://www.systec-electronic.com/blog/artikel-1/news-socketcan-docker-die-loesung
# https://blog.mbedded.ninja/programming/operating-systems/linux/how-to-use-socketcan-with-the-command-line-in-linux/#print-socketcan-info
DOCKERPID=$(docker inspect -f '{{ .State.Pid }}' can_demo)
echo $DOCKERPID
sudo modprobe can
sudo modprobe can-isotp
sudo ip link add vxcan1 type vxcan peer name vxcan0 netns $DOCKERPID
sudo modprobe can-gw
sudo cangw -A -s can0 -d vxcan1 -e
sudo cangw -A -s vxcan1 -d can0 -e
sudo ip link set vxcan1 up
sudo ip link set can0 type can bitrate 250000
sudo ip link set can0 up
sudo nsenter -t $DOCKERPID -n ip link set vxcan0 up