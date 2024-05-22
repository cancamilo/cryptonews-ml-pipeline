import os
import sys

import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.connectors.stdio import StdOutSink
from data_flow.stream_input import RabbitMQSource
from data_flow.stream_output import QdrantOutput
from feature_pipeline.data_logic.handlers import (
    CleaningHandler,
    RawDataHandler,
    ChunkingHandler,
    EmbeddingHandler
)
from db.qdrant import connection

flow = Dataflow("Streaming ingestion pipeline")
stream = op.input("input", flow, RabbitMQSource())
stream = op.map("raw dispatch", stream, RawDataHandler.handle_mq_message)
stream = op.map("clean dispatch", stream, CleaningHandler.handle_raw_message)

op.output("out", stream, StdOutSink())

op.output(
    "cleaned data insert to qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="clean"),
)
stream = op.flat_map("chunk dispatch", stream, ChunkingHandler.handle_message)
stream = op.map(
    "embedded chunk dispatch", stream, EmbeddingHandler.handle_message
)
op.output(
    "embedded data insert to qdrant",
    stream,
    QdrantOutput(connection=connection, sink_type="vector"),
)
