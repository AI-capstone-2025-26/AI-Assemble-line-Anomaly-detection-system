import Dashboard as dash
import threading as th
import time
import queue as que
import time
import random
#Program interupts
global interupt
interupt = False

#Initializing Queues
productionLine = que.Queue()
status = que.Queue()
error_marker = que.Queue()


#Main Dashboard
outputQue = th.Thread(target=dash.run_dashboard)
outputQue.start()
dash.updateFreq = 1
#Internal variables
confMat = {'tp':[], 'tn':[], 'fp':[], 'np':[], }





#REMOVE
test_data = {
    # Q1: System Log (string)
    "Terminal Output": "Hello I'm working",
    
    # Q2: Confusion Matrix (integers)
    "True Positives (TP)": 1000,          # Low number of good parts identified
    "False Positives (FP)": 20,         # High false alarm rate
    "True Negatives (TN)": 950,
    "False Negatives (FN)": 20,        # CRITICAL: 100 missed failures (Will turn red)
    
    # Q3: Process Log (string)
    "Process Log Output": "STATUS: Staying  alive.\n"
                          "Operator Intervention required on Line None."
}

def randomData():
    
    #INTERNAL: Simulates fetching real-time data from assembly line sensors/metrics.
    #Returns a dictionary of metrics and their simulated current values.

    # Simulate realistic numbers for a matrix 
    tp = random.randint(85, 98)   # Good Predictions
    fp = random.randint(1, 5)     # False Alarms
    tn = random.randint(950, 995) # Correctly ignored
    fn = random.randint(2, 10)    # Missed Failures (Critical)
    
    # --- Q1 Terminal Simulation ---
    terminal_message = f"[{time.strftime('%H:%M:%S')}] Running ML inspection cycle...\n"
    if fn > 5:
        terminal_message += "[FATAL] High FN count detected! Model review required."
    elif tp < 90:
        terminal_message += "[WARNING] Low TP count. System performance degraded."
    else:
        terminal_message += "[OK] All checks passed. Awaiting next cycle."

    # --- Q3 Terminal Simulation (Process Log) ---
    cycle_time = round(random.uniform(4.0, 7.0), 2)
    power_consumption = round(random.uniform(15.0, 25.0), 1)
    
    process_log_message = f"[{time.strftime('%H:%M:%S')}] P_ID:{random.randint(100,999)} Cycle Time: {cycle_time}s\n"
    if power_consumption > 24.0:
        process_log_message += f"[ALERT] Power high: {power_consumption}kW. Efficiency low."
    elif cycle_time > 6.5:
        process_log_message += f"[WARNING] Cycle time slow: {cycle_time}s. Throughput falling."
    else:
        process_log_message += f"[INFO] Power: {power_consumption}kW. Process nominal."


    return {
        "Terminal Output": terminal_message,
        "True Positives (TP)": tp,
        "False Positives (FP)": fp,
        "True Negatives (TN)": tn,
        "False Negatives (FN)": fn,
        "Process Log Output": process_log_message
    }



#Main loop checking for and Updating Dashboard
while interupt == False:

    #time.sleep(10)  
    dash.data_queue.put(randomData())
    #dash.data_queue.put(test_data)
    #interupt = True

    input("Press enter to update to more random data")

    #Checking if any sub process have errors
    if not outputQue.is_alive() or dash.interupt == True:
        interupt = True
        dash.exit()
    

print("euihfuhuwiehfuehfuehfuehfuehfuehfueh")

