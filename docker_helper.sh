#!/bin/bash

# Determine the platform
os=$(uname -s)
platform=$(uname -m)
device_type="jevois"
device_port="0"
config_file="none"
debug="low"
radio_port="/dev/ttyUSB0"
threaded="false"
while test $# -gt 0
do
    case "$1" in
        --camera*) device_type="camera"
            device_port="$2"
            ;;
        --config*) config_file="$2"
            echo "Using config file: $config_file"
            ;;
        --debug) debug="mid"
            echo "Debug mode enabled"
            ;;
        --debug-info) debug="high"
            echo "Verbose Debug mode enabled"
            ;;
        --radio_port*) 
            radio_port="$2"
            ;;
        --threaded) 
            echo "Threaded mode enabled"
            threaded="true"
            ;;
    esac
    shift
done
# Set Docker command based on the platform
if [[ $os == "Linux" ]]; then
    docker_cmd="docker"
    devices="--device=/dev/ttyACM0"

elif [[ $os == "Darwin" ]]; then
    docker_cmd="docker"
    devices="--device=/dev/cu.usbmodem14101"

elif [[ $os == "Windows_NT" ]]; then
    docker_cmd="docker.exe"
    devices="--device=COM3"

else
    echo "Unsupported platform: $os"
    exit 1
fi

if [[ $device_type == "camera" ]]; then
    devices="--device=/dev/video$device_port"
fi

devices="$devices --device=$radio_port"

docker_img=nriaziat/jhockey:latest

# Use the Docker command with the appropriate parameters
if [[ $config_file != "none" ]]; then
    cmd="$docker_cmd run --rm -it -v $config_file:$config_file --net=host $devices $docker_img --config $config_file --radio_port $radio_port"
else 
    cmd="$docker_cmd run --rm -it --net=host $devices $docker_img --radio_port $radio_port"
fi
if [[ $device_type == "camera" ]]; then
    cmd="$cmd --camera $device_port"
fi
if [[ $debug == "mid" ]]; then
    cmd="$cmd --debug"
elif [[ $debug == "high" ]]; then
    cmd="$cmd --debug-info"
fi
if [[ $threaded == "true" ]]; then
    cmd="$cmd --threaded"
fi
echo "Docker Command: $cmd"
$cmd