import logging
import os
from datetime import datetime
import azure.functions as func
from azure.cosmos import CosmosClient

app = func.FunctionApp()

# Cosmos DB config from App Settings
COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = "processingdb"
CONTAINER_NAME = "results"

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


@app.blob_trigger(
    arg_name="myblob",
    path="input-files/{name}",
    connection="AzureWebJobsStorage"
)
def process_blob(myblob: func.InputStream):
    logging.info(f"Blob trigger fired for: {myblob.name}")

    content = myblob.read().decode("utf-8", errors="ignore")
    error_count = content.lower().count("error")

    file_name = myblob.name.split("/")[-1]
    file_type = file_name.split(".")[-1]

    document = {
        "id": f"{file_name}-{datetime.utcnow().isoformat()}",
        "fileName": file_name,
        "fileType": file_type,          # PARTITION KEY
        "fileSizeBytes": myblob.length,
        "errorCount": error_count,
        "processedAt": datetime.utcnow().isoformat(),
        "status": "FAILED" if error_count > 0 else "SUCCESS"
    }

    container.create_item(body=document)

    logging.info("Result stored in Cosmos DB")
