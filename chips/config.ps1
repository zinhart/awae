# to be run on host via posh
docker-compose down
docker-compose up
docker-compose -f ~/chips/docker-compose.yml exec chips node --inspect=0.0.0.0:9228
