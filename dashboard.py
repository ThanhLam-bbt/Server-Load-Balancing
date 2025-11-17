import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
import time

LOG_DIR = os.path.expanduser("~/sdn_lb")
SERVER_USAGE_FILE = os.path.join(LOG_DIR, "server_usage.json")
SERVER_START = 7
SERVER_END = 12

def plot_server_usage():
    if not os.path.exists(SERVER_USAGE_FILE):
        print(f"Error: Data file not found: {SERVER_USAGE_FILE}")
        print("Please ensure that the load balancer is running and generating data.")
        return

    try:
        with open(SERVER_USAGE_FILE, 'r') as f:
            log_data = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid JSON data file. Ensure the file is not empty.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not log_data:
        print("Data file is empty. No data to plot.")
        return

    timestamps = [item['timestamp'] for item in log_data]
    
    time_labels = [datetime.fromtimestamp(ts).strftime('%H:%M:%S') for ts in timestamps]
    
    server_names = [f"server{i}" for i in range(SERVER_START, SERVER_END + 1)]
    
    plt.figure(figsize=(12, 6))
    
    for name in server_names:
        counts = [item['server_usage'].get(name, 0) for item in log_data]
        plt.plot(time_labels, counts, marker='o', label=name)

    plt.title('Server Request Count Over Time (Load Balancing)')
    plt.xlabel('Time')
    plt.ylabel('Total Request Count')
    plt.legend(loc='upper left')
    plt.grid(True)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.show()

if __name__ == '__main__':
    plot_server_usage()
