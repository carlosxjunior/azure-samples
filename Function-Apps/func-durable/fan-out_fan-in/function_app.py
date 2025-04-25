from logging.handlers import RotatingFileHandler
import azure.durable_functions as df
from collections import Counter
import azure.functions as func
from bs4 import BeautifulSoup
import requests
import logging
import time
import re
import os

def configure_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "durable_functions.log")
    
    # Clear existing log file on startup
    if os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.truncate(0)  # Empty the file
    
    # Configure logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add rotating file handler
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(file_handler)

# Initialize logging
configure_logging()

df_app = df.DFApp()  # Initialize DFApp

SPORTS = [
    "football", "basketball", "tennis", "mma", "volleyball",
    "baseball", "table_tennis", "hockey", "american_football", "gymnastics",
    "cricket", "badminton", "golf", "archery", "swimming_(sport)",
    "cycling", "boxing", "esports", "skiing", "wrestling"
]

STOP_WORDS = {
    'the', 'and', 'of', 'in', 'to', 'a', 'is', 'for', 'on', 'with', 'as', 'by',
    'that', 'was', 'are', 'it', 'be', 'at', 'this', 'have', 'from', 'or', 'an'
}

# HTTP Trigger → starts orchestrator
@df_app.route(route="start")
@df_app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    logging.info("[HTTP trigger] Received a request to start the orchestrator...")
    instance_id = await client.start_new("orchestrator", None, None)
    logging.info(f"[HTTP trigger] Orchestrator started with instance ID: {instance_id}")
    # Wait for completion (timeout after 30 sec)
    timeout = 45  # seconds
    response = await client.wait_for_completion_or_create_check_status_response(
        req,
        instance_id,
        timeout_in_milliseconds=timeout*1000
    )
    
    if isinstance(response, func.HttpResponse):
        logging.info(f"[HTTP trigger] Orchestration completed! Status: {response.status_code}")
        return response
    else:
        return func.HttpResponse(
            f"Orchestration timed out after {timeout} seconds. Status URL: {response.json()['statusQueryGetUri']}",
            status_code=202
        )

# Orchestrator → Fan-out/fan-in for all sports
@df_app.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    start = time.monotonic()
    # Fan-out: Process all sports in parallel
    logging.info("[Orchestrator] Starting to process sports...")
    tasks = [context.call_sub_orchestrator("process_sport_orchestrator", sport) for sport in SPORTS]
    
    # Fan-in: Wait for all sports to complete
    results = yield context.task_all(tasks)
    logging.info(f"[Orchestrator] All sports processed successfully after {(time.monotonic() - start):2f} seconds.")
    return results

# Sub-Orchestrator → Coordinates tasks for a single sport
@df_app.orchestration_trigger(context_name="context")
def process_sport_orchestrator(context: df.DurableOrchestrationContext):
    sport = context.get_input()
    logging.info(f"[Sub-Orchestrator] - {sport}: Processing sport...")
    # Step 1: Fetch Wikipedia page (returns HTML content)
    html_content = yield context.call_activity("fetch_wikipedia_page", sport)

    task_input = {
        "html_content": html_content,
        "sport": sport  # Pass sport name to all activities
    }
    
    # Step 2: Run all three analysis tasks in parallel
    hyperlinks_task = context.call_activity("count_hyperlinks", task_input)
    words_task = context.call_activity("get_top_words", task_input)
    letter_a_task = context.call_activity("count_letter_a", task_input)
    
    # Wait for all three tasks to complete
    hyperlinks, top_words, letter_a = yield context.task_all([
        hyperlinks_task,
        words_task,
        letter_a_task
    ])
    logging.info(f"[Sub-Orchestrator] - {sport}: Completed processing sport.")
    return {
        "sport": sport,
        "wikipedia_page": f"https://en.wikipedia.org/wiki/{sport}",
        "count_hyperlinks": hyperlinks,
        "count_letter_a": letter_a,
        "top_10_words": top_words
    }

# Activity 1: Fetch Wikipedia page
@df_app.activity_trigger(input_name="sport")
async def fetch_wikipedia_page(sport: str) -> str:
    logging.info(f"[Activity] - {sport}: Fetching Wikipedia page...")
    url = f"https://en.wikipedia.org/wiki/{sport}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text  # Return raw HTML for other activities

# Activity 2: Count hyperlinks
@df_app.activity_trigger(input_name="input")
async def count_hyperlinks(input: dict) -> int:
    sport = input["sport"]
    html_content = input["html_content"]
    logging.info(f"[Activity] - {sport}: Counting hyperlinks...")
    soup = BeautifulSoup(html_content, 'html.parser')
    n_hyperlinks = len(soup.find_all('a', href=True))
    return n_hyperlinks

# Activity 3: Count letter 'A' (case-insensitive)
@df_app.activity_trigger(input_name="input")
async def count_letter_a(input: dict) -> int:
    sport = input["sport"]
    html_content = input["html_content"]
    logging.info(f"[Activity] - {sport}: Counting letter A...")
    text = BeautifulSoup(html_content, 'html.parser').get_text().lower()
    return text.count('a')

# Activity 4: Get top 10 words (excluding STOP_WORDS)
@df_app.activity_trigger(input_name="input")
async def get_top_words(input: dict) -> dict:
    sport = input["sport"]
    html_content = input["html_content"]
    logging.info(f"[Activity] - {sport}: Getting top 10 words...")
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text().lower()
    words = re.findall(r'\b[a-z]{3,}\b', text)
    filtered_words = [word for word in words if word not in STOP_WORDS]
    word_counts = Counter(filtered_words).most_common(10)
    return {i+1: f"{word} ({count})" for i, (word, count) in enumerate(word_counts)}