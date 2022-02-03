# set user
user 					= 1000:1000

# docker image and container details
Docker_name				= $(shell whoami)/test_proxy
container_name 			= test_proxy

# forwards ports
ports 					= -p 80:80 -p 8080:8080 

build:
	@docker build . -t $(Docker_name)

no_cache:
	@docker build . -t $(Docker_name) --no-cache

bash:
	@docker run -it --rm --gpus=all $(ports) -v $(volume_dir) -v $(dataset_dir) --name $(container_name) $(Docker_name) bash || docker exec -it $(container_name) bash

run:
	@docker run -it --rm --gpus=all $(ports) -v $(volume_dir) -v $(dataset_dir) --name $(container_name) $(Docker_name) || docker exec -it $(container_name) bash

reset_migrations:
	@find . -path "*/*/migrations/*.py" -not -name "__init__.py" -delete
	@find . -path "*/*/migrations/*.pyc"  -delete
	@python django_dataset_collection_tool/manage.py makemigrations
	@python django_dataset_collection_tool/manage.py migrate