database:
	django-admin migrate
	django-admin compile_and_collect
	django-admin load_aristotle_help
	django-admin createcachetable

metadata:
	curl https://raw.githubusercontent.com/aristotle-mdr/user-documentation/draft/server/fixtures/users.yaml > /tmp/users.yaml
	curl https://raw.githubusercontent.com/aristotle-mdr/user-documentation/draft/server/fixtures/test_metadata.yaml > /tmp/metadata.yaml
	django-admin loaddata /tmp/users.yaml
	django-admin loaddata /tmp/metadata.yaml

server:
	sudo docker-compose up
