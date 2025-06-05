#!/bin/bash
curl -fsSL https://get.docker.com | bash

sudo apt-get update && sudo apt-get install uidmap dbus-user-session -y

dockerd-rootless-setuptool.sh install

docker run hello-world