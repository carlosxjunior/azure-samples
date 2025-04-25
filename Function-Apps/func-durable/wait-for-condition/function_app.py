from datetime import datetime, timedelta
import azure.durable_functions as df
import azure.functions as func
import logging

myApp = df.DFApp()

@myApp.route(route="start")
@myApp.durable_client_input(client_name="client")
async def http_trigger(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    logging.info("[HTTP trigger] Python HTTP trigger function processed a request.")

    instance_id = await client.start_new(orchestration_function_name="orchestrator_function", instance_id=None, client_input=None)
    return client.create_check_status_response(req, instance_id)

@myApp.orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    start_time = context.current_utc_datetime
    i = 1
    logging.info("[Orchestrator] Starting orchestrator function...")
    while True:
        result = yield context.call_activity(name="activity_function")
        if result:
            logging.info("[Orchestrator] Activity function returned True, stopping orchestration.")
            break
        logging.info("[Orchestrator] Activity function returned False, waiting for next check.")
        next_check = start_time + timedelta(minutes=i)
        yield context.create_timer(fire_at=next_check)
        i += 1
    logging.info("[Orchestrator] Finished orchestartor function.")
    return {"execution_count": i}

@myApp.function_name(name="activity_function")
@myApp.activity_trigger(input_name="context")
def activity_function(context):
    now = datetime.now()
    logging.info(f"[Activity] Starting activity function, now = {now.strftime('%H:%M:%S')}")
    return now.minute % 3 == 0 # Simulate a condition that returns True every 3 minutes