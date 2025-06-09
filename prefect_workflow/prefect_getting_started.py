from prefect import flow, task
import random

@task
def get_customer_ids() -> list[str]:
    # Fetch customer IDs from a database or API
    return [f"customer{n}" for n in random.choices(range(100), k=5)]

@task
def process_customer(customer_id: str) -> str:
    # Process a single customer
    return f"Processed {customer_id}"

@task
def summarize_results(results: list[str]) -> str:
    return f"Summarized {len(results)} results: {results}"

@flow(
    persist_result=True,
)
def prefect_getting_started() -> list[str]:
    customer_ids = get_customer_ids()
    # Map the process_customer task across all customer IDs
    results = process_customer.map(customer_ids)
    summary = summarize_results(results)
    return summary


if __name__ == "__main__":
    # prefect_getting_started()
    prefect_getting_started.serve(
        name="local-deploy-prefect-getting-started",
    )
