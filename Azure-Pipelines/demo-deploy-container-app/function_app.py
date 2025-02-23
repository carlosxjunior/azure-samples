import azure.functions as func
import logging

app = func.FunctionApp()

@app.function_name("HelloWorld")
@app.route(route="hello-world", methods=[func.HttpMethod.POST], auth_level=func.AuthLevel.FUNCTION)
def hello_world(req: func.HttpRequest, context=func.Context):
    logging.info(f"PYLOG: Python http trigger function {context.function_name} processed a request.")
    return func.HttpResponse(
        "Hello, World",
        status_code=200
    )