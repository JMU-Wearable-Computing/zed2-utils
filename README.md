# zed2-utils
Demo and example code working with the ZED2. These files are extensions of the [provided zed_examples from stereolabs](https://github.com/stereolabs/zed-examples/blob/master/body%20tracking/python/cv_viewer/tracking_viewer.py), each have a defined openCV and openGL folder for setting up the purpose of the camera.

# Installation of ZED SDK
## Provided is a step-by-step process for installation of the API, CUDA, and the required SDK libraries for use of the ZED camera. If the SDK and CUDA are up-to-date, then the API can be simply re-configured when needed. We recommend CUDA is pre-installed prior the the ZED SDK installation to cause less issues with their own installation if it appears in the future.

### API Installation
The API has a quick installation through the requirements.txt file provided. Install in your virtual environment or base environment through the following terminal input. This will provide a more up to date version of dependencies for the current project.

<code> pip install -r requirements.txt </code>

This will provide libraries such as opencv, opengl, and their API 'pyzed'

### CUDA
CUDA is a library for graphics processing manipulation that is required for the camera. [Install the provided CUDA toolkit here](https://developer.nvidia.com/cuda-downloads), providing the correct answers to the prompt asking for your computers configuration and then using the terminal inputs provided.

### SDK
Downloading the SDK for ZED2 to configure the camera is easy, but may take an hour or two due to the pre-processing done during configuration. This can be limited by typing 'n' for no at any point of request during the installation. This installation will be defined for Ubuntu 18.04, but a similar windows version is provided [here for more specific details on windows installation](https://www.stereolabs.com/docs/installation/windows/). 

First, [go to the installation website](https://www.stereolabs.com/developers/release/) and download the SDK for your Ubuntu version. Once downloaded, go to your configured downloads folder and run the following 

<code> chmod +x ZED_SDK_Ubuntu18_cuda11.x_vx.x.x.zstd.run </code>

<code> ./ZED_SDK_Ubuntu18_cuda11.x_vx.x.x.zstd.run </code>

Running this can take a couple hours, but requires input after each stage for configuration of its systems and for calibration.

After it is finally installed, the ZED camera can be manipulated using the pyzed library.
