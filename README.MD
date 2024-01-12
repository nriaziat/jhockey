# Project Name

JHockey Game Manager

## Prerequisites

- Python (version 3.11.5)
- fastapi
- nicegui
- numpy
- opencv_contrib_python

## Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Install the required dependencies by running the following command:

    ```shell
    conda create -n jhockey
    conda activate jhockey
    pip install -r requirements.txt
    pip install .
    ```

Or, using Docker

    ```shell
    docker build . --tag jhockey:latest
    docker run -it --rm --device /dev/video0 jhockey 
    ```

## Usage

Run main.py. A GUI will be hosted at localhost:8080. Optionally, pass an int value to the command with "--camera" to choose a specific camera index. 

## License

This project is licensed under the [License Name] - see the [LICENSE](LICENSE) file for details.

## Contact

- Naveed Riaziat - [Email](mailto:nriaziatl@jhu.edu)

