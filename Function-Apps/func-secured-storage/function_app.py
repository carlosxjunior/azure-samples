import azure.functions as func
import logging
import os

from azureBlobClient import AzureBlobClient

app = func.FunctionApp()

@app.route(route="http-example", auth_level=func.AuthLevel.FUNCTION)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request in route 'http-example'.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
@app.route(route="upload-blob", auth_level=func.AuthLevel.FUNCTION)
def UploadBlob(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request in route 'upload-blob'.")
    req_body = req.get_json()
    container_name = req_body.get("container")
    blob_name = req_body.get("blob")

    if not container_name or not blob_name:
        return func.HttpResponse(
            "Please specify the parameters 'container' and 'blob' in the request body.",
            status_code=400
        )

    with open("sample_data.json", "r") as json_file:
            data = json_file.read()

    try:
        azure_blob_client = AzureBlobClient(connection_string=os.getenv("AzureWebJobsStorage"))
        azure_blob_client.upload_blob(container_name, blob_name, data=data.encode("utf-8"))
        return func.HttpResponse(f"Blob '{blob_name}' uploaded successfully.", status_code=200)
    except Exception as e:
        logging.error(f"Error uploading blob: {e}")
        return func.HttpResponse(f"Error uploading blob: {e}", status_code=500)