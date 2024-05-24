# Data Ingestion Pipeline

The [entry point](./main.py) of the lambda function contains the logic for extracting the data. It accepts a parameter `mode` that defines whether the extraction is run the daily or in backfill mode. 

The daily mode will extract only data for the current day. This mode is ideal for using an AWS EventBridge that schedules calls everyday at a given time.

On the other hand, the backfill mode will extract data for several days in the past and can be used for initializing both the mongoDB and the vector database with some data. 

Once the data is extracted from every source, it will be dumped to a mongoDB replica set.


## Testing locally

The [Makefile](/data_ingestion_pipeline/Makefile) inside this folder can be used to run the required services to start ingesting data. 

First you need to start the docker containers:

```
make start
```

This command will spin up the MongoDb replica set and the lambda function locally. 

Once the services are up, the extraction of news can be triggered.
For extracting news for the current day use:

```
make local-test MODE=daily
```

For extracting news several days in the past use the backfill mode:

```
make local-test MODE=backfill
```

For stopping all running containers:

```
make strop-all
```

After the execution of the steps above, you should have articles data available in the MongoDB.

## Running in the cloud

TBD