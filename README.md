# G2Hack

## Kafka Setup
run this command in root directory of the project
```bash
# start zookeeper and kafka
 docker-compose up -d
```
shutdown the kafka and zookeeper
```bash
# stop zookeeper and kafka
 docker-compose down
```

## run scrapper
```bash
# Pull the image
docker pull pes1ug21cs364/g2-hack:scrape-products
# run the image
docker run --network="host" scrape-products
```
## run consumer
```bash
# Pull the product consumer
docker pull pes1ug21cs364/g2-hack:software-consumer
# run the image
docker run --network="host" consumer-image
```

## Project Architecture
![image](https://github.com/Manoj-2702/G2Hack/assets/92267208/c6b9b71b-4540-45ab-b600-c4ede2bec064)

## Kafka Architecture
![image](https://github.com/Manoj-2702/G2Hack/assets/92267208/4ce38d65-ebe1-4a2f-8db8-ea07ac804fc9)


