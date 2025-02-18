import azure.functions as func
import logging
from pyrfc import Connection

app = func.FunctionApp()

@app.route(route="call-pyrfc", auth_level=func.AuthLevel.ANONYMOUS)
def PyrfcExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # ashost="10.0.0.1", sysnr="00", client="100", user="me", passwd="secret"
    try:
        ashost = req.get_json().get("ashost")
        sysnr = req.get_json().get("sysnr")
        client = req.get_json().get("client")
        user = req.get_json().get("user")
        passwd = req.get_json().get("passwd")
        if not all([ashost, sysnr, client, user, passwd]):
            return func.HttpResponse(
                "Please provide all required parameters in the request body: ashost, sysnr, client, user, passwd.",
                status_code=400
            )
    except Exception as e:
        return func.HttpResponse(
            f"Due to an excepction, the expected parameters could not be retrieved from request body: ashost, sysnr, client, user, passwd.\n\nError: {str(e)}",
            status_code=500
        )

    error = None
    try:
        conn = Connection(ashost=ashost, sysnr=sysnr, client=client, user=user, passwd=passwd)
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