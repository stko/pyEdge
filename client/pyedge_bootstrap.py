import sys
import pika
import uuid
import json
import argparse
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from python_on_whales import docker

class PyeBootstrap:

    def __init__(self,host,port,user,password):
        self.read_local_config()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(user, password)))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def read_local_config(self):
        self.local_config={
            "position":"4711"
        }

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def get_config(self,duni_id):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='bootstrap',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                content_type="application/json"
            ),
            body=json.dumps({
                "duni_id":duni_id,
                "position": self.local_config["position"]
            }))
        self.connection.process_data_events(time_limit=None)
        response=self.response.decode()
        return json.loads(response)

    def calculate_docker_compose(self, input_text):
        global args
        known_placeholders = {
            "duni_id" : args.duniid,
            "position": self.local_config["position"]
        }
        for key, value in known_placeholders.items():
            input_text=input_text.replace("%"+key+"%",value)
        try:
            dc_object=load(input_text, Loader=Loader)
        except:
            print("FATAL: corrupt docker-compose data!")
            sys.exit(127)
        for service, this_service in dc_object["services"].items():
            elements = service.split("_")
            if len(elements)>1 and elements[-1].isnumeric(): # the last value is a number
                    service_name="_".join(elements[:-1])
                    service_index=elements[-1]
            else:
                service_name=service
                service_index="1"
            this_service["container_name"]=service
            if "environment" not in this_service:
                this_service["environment"]=[]
            new_env="MODULE_NAME="+service_name
            if new_env not in this_service["environment"]:
                this_service["environment"].append(new_env)
            new_env="MODULE_INDEX="+service_index
            if new_env not in this_service["environment"]:
                this_service["environment"].append(new_env)
            new_env="DUNI_ID="+args.duniid
            if new_env not in this_service["environment"]:
                this_service["environment"].append(new_env)
        input_text=dump(dc_object)

        return input_text

    def write_docker_compose(self,config_test):
        try:
            with open("docker-compose.yml","w") as fout:
                fout.write(config_test)
        except Exception as ex:
            print(str(ex))

    def close(self):
        if self.connection:
             self.connection.close()


parser=argparse.ArgumentParser()
parser.add_argument("--host",help="the RabbitMQ Exchange Server", default="localhost")
parser.add_argument("--port",help="the Server Port", default=5672, type=int)
parser.add_argument("--user",help="the Server User Name", default="guest")
parser.add_argument("--password",help="the Server Password", default="guest")
parser.add_argument("--duniid",help="the Duni ID (for debugging only)", default=hex(uuid.getnode()).upper())
args=parser.parse_args()



bootstrap = PyeBootstrap(args.host,args.port,args.user,args.password)
print(" try to get initial config")
response = bootstrap.get_config(args.duniid)
print(" [.] Got %s" % response)
new_cd=bootstrap.calculate_docker_compose(response["docker-compose"])
bootstrap.write_docker_compose(new_cd)
bootstrap.close()
# let's dance
# first make the base module
docker.build("./pythonbuilder",tags=["pythonbuilder"])
#and then do the rest
docker.compose.up()
