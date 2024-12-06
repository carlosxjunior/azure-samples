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

@app.function_name("HelloYou")
@app.route(route="hello-you", methods=[func.HttpMethod.POST], auth_level=func.AuthLevel.FUNCTION)
def hello_you(req: func.HttpRequest, context=func.Context):
    logging.info(f"PYLOG: Python http trigger function {context.function_name} processed a request.")
    you = req.params.get("you")
    return func.HttpResponse(
        f"Hello, {you}",
        status_code=200
    )