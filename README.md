# News ML Pipelines for RAG

A real time machine learning system that processes cryptocurrency news from multiple sources to enable retrieval augmented generation and data collection for LLMs finetuning. By providing access to recent news, it offers an up-to-date, comprehensive overview of the cryptocurrency market through text summarization, sentiment analysis and RAG.


<br>
<p align="center">
    <img src="media/ml-flow-chart.svg" alt="System Architecture" title="System Architecture">
</p>
<br>

Following an event based architecture, each time text data is fetched, it becomes available through in an event stream that is further processed and made available in different forms for being consumed for both training and inference through a feature store. With this approach, the system can be further expanded to accept different streams of data such as audio, video, price feeds, etc.

The system architecture is structured according to a multiple pipeline design pattern composed of the following modules:

- Data ingestion: Uses an aws lambda function to perform the extraction of news data from different sources. The function can be triggered based on events or on a given timer. The extracted data is saved to a mongoDB. The changes made to the mongoDB are listened by a service following the Change Data Capture pattern. The service job is to send the captured data to RabbitMQ.

- Feature pipeline: This is the streaming pipeline in charge of listening and postprocessing the data coming from the RabbitMQ queue. The text postprocessing consist of cleaning, chunking and embedding. Finally, the text data is saved to a vector database along with the embeddings for each chunk.

- Training: TBD
- Inference: TBD

Every module in this repository can be tested locally or deployed to AWS (TBD).

Repository outline:

- [Tech Stack](#tech-stack)
- [Test locally](#test-locally)
- [Data ingestion Pipeline](#data-ingestion-pipeline)
    - [MongoDB Sync](#mongodb-sync)
- [Feature Pipeline](#feature-pipeline)
- [Training](#training-pipeline)
- [Inference](#inference)

## Tech Stack description

AWS Lambda: I chose AWS Lambda for its flexibility and cost-effectiveness. It's ideal since it's stateless and can easily handle the event-driven or time-based triggers for data extraction.

MongoDB: This database is the choice for storing document-like data such as text. It's particularly useful for this system because it simplifies the implementation of the data capture pattern.

RabbitQM: This is a robust message broker that provides a common platform for applications to send and receive messages. It's chosen for its reliability, scalability, and flexibility. In this system, it's used to handle the flow of data from the data ingestion module to the feature pipeline, ensuring that messages don't get lost even in high throughput scenarios. It supports multiple messaging protocols and can be deployed in distributed and federated configurations, making it a versatile choice for managing data flow in real-time machine learning systems.

Bytewax: This tool allows constructing real-time streaming pipelines in python, enabling to deliver advanced AI use cases in any environment, from edge computing to cloud-based systems.

Qdrant: TDB

CometML: TDB

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

## Feature Pipeline

The code for this module is under the [feature_pipeline](/feature_pipeline) folder. 

## Training

## Inference 