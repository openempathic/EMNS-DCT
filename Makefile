# set user
user 					= 1000:1000

# docker image and container details
Docker_name				= $(shell whoami)/dataset_collection_tool
container_name 			= dataset_collection_tool

# forwards ports
ports 					= -p 8000:8000

# set volume directory
volume_dir 				= $(shell pwd):/home/docker/projects
dataset_dir 			= /media/$(shell whoami)/DATA/Datasets/:/Datasets



build:
	@docker build . -t $(Docker_name)

no_cache:
	@docker build . -t $(Docker_name) --no-cache

bash:
	@docker run -it --rm --gpus=all $(ports) -v $(volume_dir) -v $(dataset_dir) --name $(container_name) $(Docker_name) bash || docker exec -it $(container_name) bash

run:
	@docker run -it --rm --gpus=all $(ports) -v $(volume_dir) -v $(dataset_dir) --name $(container_name) $(Docker_name) || docker exec -it $(container_name) bash