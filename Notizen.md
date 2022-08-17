

Get config from usb
store it
get docker container list from CCS
.venv/bin/python rpc_client.py localhost

# mit docker bootstrap
docker-compose up parent_company_rabbitmq
../.venv/bin/python backbone_emu.py 
 ../.venv/bin/python pyedge_bootstrap.py --host localhost --user myuser --password mypassword --port 5673


# ohne docker bootstrap, nur ein Datenaustausch test

CAN- Bus vorheizen:

  sudo insmod ~/Desktop/workcopies/pysotp/can-isotp/net/can/can-isotp.ko
  sudo ip link set vcan0 type can bitrate 125000
  sudo ip link set vcan0 up


CAN im Container:

DOCKERPID=$(docker inspect -f '{{ .State.Pid }}' can_demo)
sudo ip link add vxcan1 type vxcan peer name vxcan0 netns $DOCKERPID
sudo ip link set vxcan1 up
sudo nsenter -t $DOCKERPID -n ip link set vxcan0 up


## ToDo:
* Der client muß einen unique Namen bekommen
* es muß dafür gesorgt werden, das der Container den DNS des Parent auflösen kann