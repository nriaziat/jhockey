# JHockey

## Prerequisites

- Ubuntu 20.04
- Python 3.11.5
- fastapi
- nicegui
- numpy
- opencv_contrib_python 
- Docker [optional]

## Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Install the required dependencies by running the following command:

    ```shell
    conda create -n jhockey
    conda activate jhockey
    pip install -r requirements.txt
    pip install .
    python3 main.py
    ```

    Or, to build with Docker on x86
    ```shell
    docker build . --tag jhockey:latest
    docker run -it --rm --device /dev/ttyACM0 jhockey 
    docker run -it --rm --device /dev/video0 jhockey --camera 0
    ```
    
    Or, to build with Docker on Raspberry Pi. For performance reasons, it is not recommended to run without the JeVois. 
    ```shell
    docker build . --platform=aarch64 --tag jhockey:rpi
    docker run -it --rm --device /dev/ttyACM0 jhockey:rpi 
    ```

    Or, to pull the DockerHub image:
    ```shell
    ./docker_helper.sh # will pull appropriate image from Docker Hub
    ```
### Raspberry Pi Setup

If running with Docker on a Raspberry Pi, please follow the instructions [here](https://docs.docker.com/engine/install/debian/) for 64-bit OS (32-bit is not implemented for this project). It is recommended to run the [Linux Post-Install](https://docs.docker.com/engine/install/linux-postinstall/) to avoid using Docker with sudo.

## XBee Setup

See [ZigBee_Setup.md](./micropython/ZigBee_Setup.md) for instructions on how to set up the XBee radios.

## Usage

Run main.py or use Docker. A GUI will be hosted at localhost:8080. There are several command line arguments that can be used to edit the match length (in seconds), enable puck tracking, use an external camera instead of the JeVois, and pass custom config files. When passing config files through Docker ensure ```docker -v /path/to/your/config``` is included with the command line arguments. For more information, use ```--help, -h```.

Arguments: ```--camera, --config, --match_length, --puck_tracking, --debug, --debug_info, --radio_port```

All positional types use integer centimeters and centiradians as default units. Time is given in seconds by default, but broadcasted to the robots in integer deciseconds. 

Message Format: ```>TIME_LEFT[4] ENABLED[1] ... ID[2] X[3] Y[3] THETA[3] ... \n``` without spaces.

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE](LICENSE) file for details.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
