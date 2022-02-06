docker-compose build
docker-compose up -d

cp -r ./docker/musician ./src
cp -r ./docker/orchestra ./src

docker-compose exec dj-musician bash scripts/setup.sh
docker-compose exec dj-orchestra bash scripts/setup.sh

code -a ./src/musician/django-musician && code -a ./src/orchestra