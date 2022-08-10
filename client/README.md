

to be able to run the new docker compose (and not the old docker-compose), follow the instructions on

https://www.rockyourcode.com/how-to-install-docker-compose-v2-on-linux-2021/


# create the docker plugins directory if it doesn't exist yet
mkdir -p ~/.docker/cli-plugins
# download the CLI into the plugins directory
curl -sSL https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
# make the CLI executable
chmod +x ~/.docker/cli-plugins/docker-compose