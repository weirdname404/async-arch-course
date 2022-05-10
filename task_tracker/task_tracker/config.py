from dataclasses import dataclass


@dataclass
class Config:
    host: str = '0.0.0.0'
    port: int = 8080
    mongo_connection_str: str = "mongodb://127.0.0.1:27017"
    mongo_db_name: str = "tasks"


config = Config()
