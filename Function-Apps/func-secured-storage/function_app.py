import azure.functions as func
import logging

from azureBlobClient import AzureBlobClient

azure_blob_client = AzureBlobClient(account_name="rgsecurefuncdemo8a18")

app = func.FunctionApp()

@app.route(route="http_example", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="HttpExample")
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

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

@app.route("read_blob", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="ReadBlob")
def ReadBlob(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request to read a blob.")

    container_name = req.params.get("container_name")
    blob_name = req.params.get("blob_name")

    if not container_name or not blob_name:
        return func.HttpResponse(
            "Please pass both container_name and blob_name in the query string",
            status_code=400
        )

    try:
        blob_content = azure_blob_client.read_blob(container_name, blob_name)
        return func.HttpResponse(blob_content, status_code=200)
    except Exception as e:
        logging.error(f"Error reading blob: {e}")
        return func.HttpResponse(f"Error reading blob: {e}", status_code=500)
    

"""@app.route("upload_blob", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="UploadBlob")
def UploadBlob(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request to upload a blob.")

    container_name = req.params.get("container_name")
    blob_name = req.params.get("blob_name")
    file_name = req.params.get("file_name")
    #file = req.files.get(file_name)
    logging.info(f"{container_name}, {blob_name}, {file_name}")

    if not container_name or not blob_name:
        return func.HttpResponse(
            "Please pass container_name, blob_name and file in the request",
            status_code=400
        )

    with open("sample_data.json", "r") as json_file:
            data = json_file.read()

    try:
        azure_blob_client.upload_blob(container_name, blob_name, data=data.encode("utf-8"))
        return func.HttpResponse(f"Blob '{blob_name}' uploaded successfully.", status_code=200)
    except Exception as e:
        logging.error(f"Error uploading blob: {e}")
        return func.HttpResponse(f"Error uploading blob: {e}", status_code=500)"""