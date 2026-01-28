import logging
import os
from azure.cosmos import CosmosClient
import azure.functions as func
from datetime import datetime

def main(myblob: func.InputStream):
    logging.info(f"Processing file: {myblob.name}")

    content = myblob.read().decode("utf-8")
    error_count = content.count("ERROR")

    status = "FAILED" if error_count > 5 else "SUCCESS"

    client = CosmosClient(
        os.environ["COSMOS_ENDPOINT"],
        os.environ["COSMOS_KEY"]
    )

    database = client.get_database_client("processingdb")
    container = database.get_container_client("results")

    container.create_item({
        "id": f"{myblob.name}-{datetime.utcnow().timestamp()}",
        "fileName": myblob.name,
        "fileType": "log",
        "errorCount": error_count,
        "status": status,
        "processedAt": datetime.utcnow().isoformat()
    })

    logging.info("Result saved to Cosmos DB")

    if status == "FAILED":
        raise Exception("High error count detected")