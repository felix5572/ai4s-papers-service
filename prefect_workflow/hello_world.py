from prefect import flow


@flow(log_prints=True)
def hello_world(name: str = "world", goodbye: bool = False):
    print(f"Hello {name} from Prefect!")

    if goodbye:
        print(f"Goodbye {name}!")
    return f"Hello {name} from Prefect!"