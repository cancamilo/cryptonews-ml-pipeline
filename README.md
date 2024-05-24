# ML Pipelines for RAG

A real time machine learning system that processes news from multiple sources to enable retrieval augmented generation and data collection for LLMs finetuning.

<p align="center">
    <img src="media/ml-flow-chart.png" alt="System Architecture" title="System Architecture">
</p>

With a real time approach, the text data becomes available in different forms for being consumed for both training and inference through a feature store. This is preferred over a batching strategy which would require a more complex synchronization between databases.

The system architecture is structured according to a multiple pipeline design pattern composed of the following modules:

- Data ingestion: Uses an aws lambda function to perform the extraction of news data from different sources. The function can be triggered based on events or on a given timer. The extracted data is saved to a mongoDB. The changes made to the mongoDB are listened by a service following the Change Data Capture pattern. The service job is to send the captured data to RabbitMQ.

- Feature pipeline: This is the streaming pipeline in charge of listening and postprocessing the data coming from the RabbitMQ queue. The text postprocessing consist of cleaning, chunking and embedding. Finally, the text data is saved to a vector database.

- Training: TBD
- Inference: TBD

Every module in this repository can be tested locally or deployed to AWS (TBD).

Repository outline:

- [Tech Stack](#tech-stack)
- [Data ingestion Pipeline](#data-ingestion-pipeline)
    - [MongoDB Sync](#mongodb-sync)
    - [Running locally](#running-locally)
- [Feature Pipeline](#feature-pipeline)
- [Training](#training-pipeline)
- [Inference](#inference)

## Tech Stack description

AWS Lambda: versatility, low cost. Stateless.

MongoDb: good for saving documents such as text. Easy to implement the data capture pattern.

Bytewax: Build real-time streaming pipelines 5x faster and deliver cutting-edge AI use cases in any environment, from edge to cloud.

AWS Lambda: I chose AWS Lambda for its flexibility and cost-effectiveness. It's ideal since it's stateless and can easily handle the event-driven or time-based triggers for data extraction.

MongoDB: This database is the choice for storing document-like data such as text. It's particularly useful for this system because it simplifies the implementation of the data capture pattern.

Bytewax: This tool allows constructing real-time streaming pipelines in python, enabling to deliver advanced AI use cases in any environment, from edge computing to cloud-based systems.

## Data Ingestion Pipeline

The code for this module is under the [data_ingestion_pipeline](/data_ingestion_pipeline/) folder. This is the starting point where the news data is collected in the database. 

The lambda function can be triggered by an event such as calling it directly via POST request or by setting up a scheduled call that triggers the function on a given time interval. 

Currently, there are two different sources of data:

- Coin telegraph: Articles are scrapped from the coin telegraph website.
- Telegram channels: Data fetched from news channels providing cryptocurrency related news.

However, the code can be extended to accept any additional source of news data.

Check the module [README](/data_ingestion_pipeline/README) for details on the code and running the service.

### MongoDB sync

This submodule is part of the data ingestion pipeline. This standalone service listens to the insert operations in the MongoDB and forwards these changes to the RabbitMQ queue. The code is found under [mongodb_sync](/mongodb_sync). 

### Running locally
## Feature Pipeline

## Training

## Inference 