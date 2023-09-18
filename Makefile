 # set user
user 					= 1000:1000

# docker image and container details
Docker_name				= $(shell whoami)/dataset_collection_tool
container_name 			= dataset_collection_tool

# forwards ports
ports 					= --network host

# set volume directory
volume_dir 				= $(shell pwd):/app
dataset_dir 			= /media/$(shell whoami)/DATA/Datasets/:/Datasets



build:
	@docker-compose -f docker-compose-deploy.yml build

no_cache:
	@docker build . -t $(Docker_name) --no-cache

bash:
	@docker run -it --rm --gpus=all $(ports) -v $(volume_dir) -v $(dataset_dir) --name $(container_name) $(Docker_name) bash || docker exec -it $(container_name) bash

run:
	@docker-compose -f docker-compose-deploy.yml up -d

run_debug:
	@docker-compose -f docker-compose.yml up

down:
	@docker-compose -f docker-compose-deploy.yml down

restart:
	@docker-compose -f docker-compose-deploy.yml restart

debug:
	@docker-compose -f docker-compose.yml up