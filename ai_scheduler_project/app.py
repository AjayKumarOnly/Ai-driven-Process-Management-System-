from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from scheduler.rl_scheduler import run_rl_scheduler  # Your RL scheduler module
from models.ml_burst import predict_burst_time

app = Flask(__name__)

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

rf_model_path = os.path.join(MODEL_DIR, 'burst_time_predictor.joblib')
if not os.path.exists(rf_model_path):
    rf_model_path = os.path.join(BASE_DIR, 'burst_time_predictor.joblib')

scaler_path = os.path.join(MODEL_DIR, 'feature_scaler.joblib')
if not os.path.exists(scaler_path):
    scaler_path = os.path.join(BASE_DIR, 'feature_scaler.joblib')

# Load the RandomForest model and other necessary resources
rf_model = joblib.load(rf_model_path)
scaler = joblib.load(scaler_path)

# Define the feature names used in the model
FEATURE_NAMES = [
    'io_write_bytes',
    'num_ctx_switches_voluntary',
    'cpu_percent',
    'io_read_bytes',
    'io_read_count',
    'io_write_count'
]

@app.route('/')
def index():
    return render_template('index.html')  # Your HTML form

import logging

# Configure logging to print debug information
logging.basicConfig(level=logging.DEBUG)

@app.route('/schedule', methods=['POST'])
def schedule():
    try:
        # Step 1: Receive data
        data = request.get_json()

        # Log received data to ensure it is correct
        logging.debug(f"Received data: {data}")

        processes = data['processes']
        algorithm = data['algorithm']

        # Step 2: Predict burst times for the incoming processes
        for process in processes:
            process_features = [
                process['io_write_bytes'],
                process['num_ctx_switches_voluntary'],
                process['cpu_percent'],
                process['io_read_bytes'],
                process['io_read_count'],
                process['io_write_count']
            ]
            predicted_burst_time = predict_burst_time(process_features)
            process['predicted_burst_time'] = predicted_burst_time

        # Step 3: Select scheduling algorithm (e.g., FCFS, SJF, RL)
        logging.debug(f"Scheduling algorithm selected: {algorithm}")

        if algorithm == 'fcfs':
            result = fcfs_scheduler(processes)
        elif algorithm == 'sjf':
            result = sjf_scheduler(processes)
        elif algorithm == 'rl':
            # Format process list to include 'features' key for RL scheduler
            formatted_processes = []
            for proc in processes:
                features = [
                    proc['io_write_bytes'],
                    proc['num_ctx_switches_voluntary'],
                    proc['cpu_percent'],
                    proc['io_read_bytes'],
                    proc['io_read_count'],
                    proc['io_write_count']
                ]
                formatted_processes.append({
                    'arrival_time': proc['arrival_time'],
                    'features': features,
                    'pid': proc['pid']
                })

            result = run_rl_scheduler(formatted_processes)

        else:
            raise ValueError(f"Unknown algorithm selected: {algorithm}")

        logging.debug(f"Scheduling result: {result}")

        # Step 4: Return scheduling results
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error during scheduling: {str(e)}")
        return jsonify({'error': str(e)}), 500




def fcfs_scheduler(processes):
    # Simple FCFS scheduling based on arrival times
    processes.sort(key=lambda p: p['arrival_time'])
    
    current_time = 0
    completed_processes = []
    
    for proc in processes:
        # If CPU is idle and process hasn't arrived yet, advance time
        if proc['arrival_time'] > current_time:
            current_time = proc['arrival_time']

        completion_time = current_time + proc['predicted_burst_time']
        turnaround_time = max(0, completion_time - proc['arrival_time'])
        waiting_time = max(0, turnaround_time - proc['predicted_burst_time'])
        
        completed_processes.append({
            'pid': proc['pid'],
            'arrival_time': proc['arrival_time'],
            'burst_time': proc['predicted_burst_time'],
            'completion_time': completion_time,
            'turnaround_time': turnaround_time,
            'waiting_time': waiting_time
        })
        
        current_time = completion_time
    
    avg_waiting_time = np.mean([p['waiting_time'] for p in completed_processes])
    return {
        'schedule': completed_processes,
        'avg_waiting_time': avg_waiting_time
    }

def sjf_scheduler(processes):
    # Shortest Job First Scheduling (Non-preemptive)
    # Only selects processes that have already arrived at current_time
    remaining = list(processes)  # work on a copy
    current_time = 0
    completed_processes = []

    while remaining:
        # Processes available (arrived) by current_time
        available = [p for p in remaining if p['arrival_time'] <= current_time]

        if not available:
            # CPU idle — jump forward to the next arriving process
            current_time = min(p['arrival_time'] for p in remaining)
            continue

        # Pick the shortest job among arrived processes
        proc = min(available, key=lambda p: p['predicted_burst_time'])
        remaining.remove(proc)

        completion_time = current_time + proc['predicted_burst_time']
        turnaround_time = max(0, completion_time - proc['arrival_time'])
        waiting_time = max(0, turnaround_time - proc['predicted_burst_time'])

        completed_processes.append({
            'pid': proc['pid'],
            'arrival_time': proc['arrival_time'],
            'burst_time': proc['predicted_burst_time'],
            'completion_time': completion_time,
            'turnaround_time': turnaround_time,
            'waiting_time': waiting_time
        })

        current_time = completion_time

    avg_waiting_time = np.mean([p['waiting_time'] for p in completed_processes])
    return {
        'schedule': completed_processes,
        'avg_waiting_time': avg_waiting_time
    }



if __name__ == '__main__':
    app.run(debug=True)
