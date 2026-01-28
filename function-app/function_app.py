import logging
import azure.functions as func

logging.warning("FUNCTION APP LOADED.")

app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob",
    path="input-files/{name}",
    connection="AzureWebJobsStorage"
)
def process_blob(myblob: func.InputStream):
    logging.info(f"bLOB TRIGGERED:{myblob.name}")