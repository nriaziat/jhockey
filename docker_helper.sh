#!/bin/bash

# Determine the platform
os=$(uname -s)
platform=$(uname -m)
device_type="jevois"
while test $# -gt 0
do
    case "$1" in
        --camera*) device_type="camera"
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
    devices="--device=/dev/cu.usbmodem*"

elif [[ $os == "Windows_NT" ]]; then
    docker_cmd="docker.exe"
    devices="--device=COM3"

else
    echo "Unsupported platform: $os"
    exit 1
fi

if [[ $device_type == "camera" ]]; then
    devices="--device=/dev/video0"
fi

if [[ $platform == "x86_64" ]]; then
    docker_img=nriaziat/jhockey:latest
elif [[ $platform == "aarch64" ]]; then
    docker_img=nriaziat/jhockey:rpi
elif [[ $platform == "arm64" ]]; then
    echo "Running on Apple Silicon should use Rosetta."
    docker_img=nriaziat/jhockey
else
    echo "Unsupported platform: $platform"
    exit 1
fi

# Use the Docker command with the appropriate parameters
cmd="$docker_cmd run --rm -it --net=host $devices $docker_img $@"
echo $cmd
$cmd