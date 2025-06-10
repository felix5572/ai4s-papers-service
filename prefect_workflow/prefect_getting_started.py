from prefect import flow, task
import random
from prefect.artifacts import create_markdown_artifact

@task
def get_customer_ids() -> list[str]:
    # Fetch customer IDs from a database or API
    return [f"customer{n}" for n in random.choices(range(100), k=3)]

@task
def process_customer(customer_id: str) -> str:
    # Process a single customer
    return f"Processed {customer_id}"

@task
def summarize_results(results: list[str]) -> str:
    return f"Summarized {len(results)} results: {results}"

@flow(
    persist_result=True,
    # result_storage="s3-bucket/sealos-bja-prefect-storage-s3",
)
def prefect_getting_started(
    s3_object_key: str = "test.txt",
    s3_bucket_endpoint: str = "https://deepmodeling-docs-r2.deepmd.us",
) -> list[str]:

    s3_object_url = f"{s3_bucket_endpoint}/{s3_object_key}"
    print(f"s3_object_url: {s3_object_url}")

    customer_ids = get_customer_ids()
    # Map the process_customer task across all customer IDs
    results = process_customer.map(customer_ids)
    summary = summarize_results(results)

    md_uuid = create_markdown_artifact(
        key="return-value", 
        markdown=summary + "\n" + s3_object_url,
        description="return value: summary of results",
    )
    return_value = {
        's3_object_url': s3_object_url,
        'customer_ids': customer_ids,
        'md_uuid': md_uuid,
        'summary': summary,
    }
    return return_value


if __name__ == "__main__":
    # prefect_getting_started()
    prefect_getting_started.serve(
        name="local-deploy-prefect-getting-started",
    )
