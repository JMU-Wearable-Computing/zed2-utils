# zed2-utils
Demo and example code working with the ZED2. These files are extensions of the [provided zed_examples from stereolabs](https://github.com/stereolabs/zed-examples/blob/master/body%20tracking/python/cv_viewer/tracking_viewer.py), each have a defined openCV and openGL folder for setting up the purpose of the camera.

# Installation of ZED SDK ; LINUX Installation
## Provided is a step-by-step process for installation of the API, CUDA, and the required SDK libraries for use of the ZED camera. If the SDK and CUDA are up-to-date, then the API can be simply re-configured when needed. We recommend CUDA is pre-installed prior the the ZED SDK installation to cause less issues with their own installation if it appears in the future.

### API Installation
The API has a quick installation through the requirements.txt file provided and a prior installation of scikit-build. Install in your virtual environment or base environment through the following terminal input. This will provide a more up to date version of dependencies for the current project. This could take up to 10-20 minutes.

<code> pip install --upgrade pip </code>

<code> pip install scikit-build </code>

<code> pip install Cmake </code>

<code> pip install -r requirements.txt </code>

This will provide libraries such as opencv, opengl, and their API 'pyzed'

### CUDA
CUDA is a library for graphics processing manipulation that is required for the camera. [Install the provided CUDA toolkit here](https://developer.nvidia.com/cuda-downloads), providing the correct answers to the prompt asking for your computers configuration. After provinding the correct input, then use the terminal inputs provided.

Additionally, when running <code> sudo apt-get -y install cuda </code>, I used aptitude to resolve dependency issues (<code> sudo aptitude -y install cuda </code>). If aptitude is not installed, make sure to do <code> sudo apt-get install aptitude </code>

For an example, our Ubuntu 18.04 Linux OS and x86_64 architecture provided the following code output for installation of CUDA

<code> wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin </code>

<code> sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600 </code>

<code> wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu1804-12-1-local_12.1.0-530.30.02-1_amd64.deb </code>

<code> sudo dpkg -i cuda-repo-ubuntu1804-12-1-local_12.1.0-530.30.02-1_amd64.deb </code>

<code> sudo cp /var/cuda-repo-ubuntu1804-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/ </code>

<code> sudo apt-get update </code>

<code> sudo apt-get -y install cuda </code>

### SDK
Downloading the SDK for ZED2 to configure the camera is easy, but may take an hour or two due to the pre-processing done during configuration. This can be limited by typing 'n' for no at any point of request during the installation. This installation will be defined for Ubuntu 18.04, but a similar windows version is provided [here for more specific details on windows installation](https://www.stereolabs.com/docs/installation/windows/). 

First, [go to the installation website](https://www.stereolabs.com/developers/release/) and download the SDK for your Ubuntu and CUDA version. Once downloaded, go to your configured downloads folder and run the following 

<code> chmod +x ZED_SDK_Ubuntu18_cuda11.x_vx.x.x.zstd.run </code>

<code> sudo apt install zstd </code>

<code> ./ZED_SDK_Ubuntu18_cuda11.x_vx.x.x.zstd.run </code>

Running this can take a couple hours, but requires input after each stage for configuration of its systems and for calibration.

After it is finally installed, the ZED camera can be manipulated using the pyzed library.

# Installation of ZED SDK ; LINUX Installation
Installation for windows is much simpler

## Install the PyCharm Community Version IDE for Python development
To install pycharm, [download the latest version]([https://www.python.org/downloads/](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC)). For the options during installation, add the bin to the PATH variables and create the .py association.

You will also want to install these dependencies for running the code.

<code> python -m pip install cython numpy opencv-python pyopengl </code>

## Install the SDK
To install the SDK, you run the executable for the SDK
1. [Download the SDK for Windows 10/11](https://download.stereolabs.com/zedsdk/3.8/cu117/win)
2. Run the executable to install the SDK and CUDA. Make sure CUDA is installed. If CUDA is not installed or you are not sure, install [CUDA 11.7 through this link](https://developer.nvidia.com/cuda-11-7-1-download-archive)

