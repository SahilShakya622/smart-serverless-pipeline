import logging
import azure.functions as func

app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob",
    path="input-files/{name}",
    connection="AzureWebJobsStorage"
)
def process_blob(myblob: func.InputStream):
    logging.info(f"Blob name: {myblob.name}")
    logging.info(f"Blob size: {myblob.length} bytes")