import azure.functions as func
import logging
from pyrfc import Connection

app = func.FunctionApp()

@app.route(route="call-pyrfc", auth_level=func.AuthLevel.ANONYMOUS)
def PyrfcExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    error = None
    try:
        conn = Connection(ashost='10.0.0.1', sysnr='00', client='100', user='me', passwd='secret')
    except Exception as e:
        error = e

    if error:
        return func.HttpResponse(
            f"Function executed successfully and returned an error:\n{error}",
            status_code=500
        )
    else:
        return func.HttpResponse(
            f"Function executed successfully.\nconn = {conn}",
            status_code=200
        )