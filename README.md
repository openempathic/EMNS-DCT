# Default

This container was tested on `Pop!_OS 20.04`.
Additinal changes may be required such as paths, please read the appropreate `README.md`.

### Prerequisite

[nvidia-container](https://github.com/NVIDIA/nvidia-docker) is needs to be installed to run on `gpu` (Nvidia gpu is required).

For instruction on how to install `nvidia-container` please follow the offical quide [HERE](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)


### Setup
```
git clone git@github.com:charisma-ai/wav2letter.git
cd wav2letter
git submodule init; git submodule update

mkdir myRecordedAudio # this step will be remove in the future

# Download pretrained models
cd dockerfiles
chmod +x download_models.sh
./download_models.sh
```

## Build container
```
cd dockerfiles
make
```

## Run container
In the `Makefile` change `volume_dir` to your working directory.
```
cd dockerfiles
make run
```

## Start container in bash
```
cd dockerfiles
make bash
```