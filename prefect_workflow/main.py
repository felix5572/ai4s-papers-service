#!/usr/bin/env python3
"""
Zeabur deployment entry point
"""
import os
from dotenv import load_dotenv
from prefect_getting_started import prefect_getting_started

def main():
    # """启动Prefect服务"""
    # port = int(os.environ.get("PORT", 4200))
    # print(f"Starting Prefect workflow service on port {port}")
    
    # 启动serve，这会保持进程运行
    prefect_getting_started.serve(
        name="zeabur-deploy-prefect-getting-started",
        # host="0.0.0.0",
        # port=port
    )

if __name__ == "__main__":
    # load_dotenv()
    main() 