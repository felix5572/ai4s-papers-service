#!/usr/bin/env python3
"""
Zeabur deployment entry point
"""
import os
from prefect import serve
from dotenv import load_dotenv
# from prefect_getting_started import prefect_getting_started
from hello_world import hello_world
from workflow_handle_pdf import workflow_handle_pdf_to_db_and_fastgpt

def main():

    
    # 启动serve，这会保持进程运行
    # prefect_getting_started.serve(
    #     name="zeabur-deploy-prefect-getting-started",
    # )

    # prefect_getting_started_deploy = prefect_getting_started.to_deployment(name="zeabur-deploy-prefect-getting-started")
    # hello_world_deploy = hello_world.to_deployment(name="zeabur-deploy-hello-world")

    # serve(prefect_getting_started_deploy, hello_world_deploy)
    workflow_handle_pdf_to_db_and_fastgpt_deploy = workflow_handle_pdf_to_db_and_fastgpt.to_deployment(
        name="zeabur-deploy-workflow-handle-pdf-to-db-and-fastgpt",
        concurrency_limit=5
        )
    hello_world_deploy = hello_world.to_deployment(name="zeabur-deploy-hello-world")
    serve(workflow_handle_pdf_to_db_and_fastgpt_deploy, hello_world_deploy)


if __name__ == "__main__":
    # load_dotenv()
    main() 