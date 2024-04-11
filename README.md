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
# run scrapper
cd scrapper
# build the image
docker build -t scrapper-image .
# run the image
docker run --network="host" scrapper-image
```

## Project Architecture
![image](https://github.com/Manoj-2702/G2Hack/assets/92267208/c6b9b71b-4540-45ab-b600-c4ede2bec064)

## Kafka Architecture
![image](https://github.com/Manoj-2702/G2Hack/assets/92267208/4ce38d65-ebe1-4a2f-8db8-ea07ac804fc9)


