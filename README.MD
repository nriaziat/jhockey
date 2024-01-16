# JHockey

## Prerequisites

- Ubuntu 20.04
- Python 3.11.5
- fastapi
- nicegui
- numpy
- opencv_contrib_python [if not using Jevois]
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

    Or, using Docker
    ```shell
    docker build . --tag jhockey:latest
    docker run -it --rm --device /dev/video0 jhockey 
    ```

## Usage

Run main.py or use Docker. A GUI will be hosted at localhost:8080. There are several command line arguments that can be used to edit the match length (in seconds), enable puck tracking, use an external camera instead of the JeVois, and pass custom config files. When passing config files through Docker ensure ```docker -v /path/to/your/config``` is included with the command line arguments. For more information, use ```--help, -h```.

Arguments: ```--camera, --config, --match_length, --puck_tracking```

All positional types use integer millimeters and milliradians as default units. Time is given in seconds by default, but broadcasted to the robots in integer nanoseconds. 


## License

This project is licensed under the GNU GPLv3 - see the [LICENSE](LICENSE) file for details.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
