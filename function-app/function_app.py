import logging
import os
from datetime import datetime

import azure.functions as func
from azure.cosmos import CosmosClient

# ---------- Cosmos DB setup ----------
COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = "processingdb"
CONTAINER_NAME = "results"

cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# ---------- Azure Function ----------
app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob",
    path="input-files/{name}",
    connection="AzureWebJobsStorage"
)
def process_blob(myblob: func.InputStream):

    logging.info(f"Blob triggered: {myblob.name}")

    # Read file content
    content = myblob.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()

    # Simple log analysis
    error_count = sum(1 for line in lines if "error" in line.lower())

    # Detect file type
    file_name = myblob.name.split("/")[-1]
    file_type = file_name.split(".")[-1]

    # Prepare result document
    document = {
        "id": f"{file_name}-{datetime.utcnow().isoformat()}",
        "fileName": file_name,
        "fileType": file_type,
        "fileSizeBytes": myblob.length,
        "errorCount": error_count,
        "processedAt": datetime.utcnow().isoformat(),
        "status": "SUCCESS"
    }

    # Store result in Cosmos DB
    container.create_item(body=document)

    logging.info(f"Result stored in Cosmos DB for file: {file_name}")
