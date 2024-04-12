# G2Hack

## Overview

This project automates the listing of B2B software products on G2, ensuring that new software is promptly and efficiently added to the G2 marketplace. By leveraging advanced web scraping techniques, real-time data streaming, and automated workflows, this system maximizes the visibility and accessibility of new software products, particularly in regions where G2 has low penetration.

## Problem Statement
G2 aims to list every B2B software product as soon as it becomes available. However, in many geographical regions, G2's visibility is low, leading to delays in software listings. This solution identifies new software products not currently listed on G2 and adds them to the platform efficiently.

## Project Goals

- # Fast and Efficient Listings: Automate the detection and listing of new software products to ensure real-time updates.
- # Global Reach: Capture and list software launches worldwide, especially from underrepresented regions.
- #Technological Innovation: Utilize modern technologies including web scraping, real-time data streams, and cloud-native services to maintain an efficient workflow.






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


