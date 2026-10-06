import os
import psutil
import time
from backend.main import app
from fastapi.testclient import TestClient

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024 # MB

print(f"Initial Memory: {get_process_memory():.2f} MB")

client = TestClient(app)

print(f"Startup Memory: {get_process_memory():.2f} MB")
time.sleep(2)
print(f"Idle Memory: {get_process_memory():.2f} MB")

# Simulate a retrieval or chat endpoint to measure peak/retrieval memory if we had a DB
# But since this is a unit test-style run, we will just measure the initialized app
print(f"Final Memory: {get_process_memory():.2f} MB")
