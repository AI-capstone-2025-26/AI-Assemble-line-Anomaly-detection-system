import tkinter as tk
from tkinter import ttk
import time
import threading 
import queue

# --- GLOBAL CONSTANTS ---
# ... (METRIC_LABELS, QUADRANT_GROUPS, initializationData remain the same) ...

METRIC_LABELS = [
    "Terminal Output",
    "True Positives (TP)",
    "False Positives (FP)",
    "True Negatives (TN)",
    "False Negatives (FN)",
    "Process Log Output"
]

QUADRANT_GROUPS = {
    "SYSTEM_LOG": METRIC_LABELS[0:1],
    "CONFUSION MATRIX": METRIC_LABELS[1:5],
    "PROCESS_LOG": METRIC_LABELS[5:6],
}

initializationData = {
    "Terminal Output": "System initialization complete. Awaiting production data...",
    "True Positives (TP)": 0,
    "False Positives (FP)": 0,
    "True Negatives (TN)": 0,
    "False Negatives (FN)": 0,
    "Process Log Output": "Process monitoring log initialized."
}


# --- GLOBAL VARIABLES (State and Widget References) ---
root_app = None 
metric_vars = {} 
accuracy_var = None
precision_var = None
f1_score_var = None
tp_label = None
fn_label = None
fp_label = None
tn_label = None
time_var = None
status_var = None
last_update_var = None
current_dashboard_data = initializationData.copy()
interupt = False
updateFreq = 1000
# --- NEW GLOBAL: The Queue ---
# The thread-safe mechanism for passing data to the main Tkinter thread.
global data_queue
data_queue = queue.Queue() 


# --- NEW GLOBAL: Polling Rate (in milliseconds) ---
QUEUE_POLL_RATE_MS = 100 


# ----------------------------------------------------------------------
# --- INTERNAL HELPER FUNCTIONS (New and Modified) ---
# ----------------------------------------------------------------------

def _check_queue(root):
    """
    Runs on the main Tkinter thread. Polls the queue for new data
    and updates the dashboard if data is found.
    """
    global current_dashboard_data
    global data_queue
    
    try:
        # Get all items currently in the queue
        while True:
            # Non-blocking get from the queue (timeout=0)
            new_data = data_queue.get_nowait()
            last_update_var.set(f"Data Last Updated: {time.strftime('%H:%M:%S')}")

            # If successful, replace the current state with the latest data
            current_dashboard_data = new_data
            data_queue.task_done()
    except queue.Empty:
        # This is the normal operation when no new data is available
        pass
    
    # Only update the GUI if new data was successfully pulled in the current cycle
    # (i.e., current_dashboard_data was modified from the queue).
    if current_dashboard_data is not initializationData:
        update_data(root)
        
    # Schedule the next queue check
    root.after(QUEUE_POLL_RATE_MS, lambda: _check_queue(root))


# The rest of the helper functions (_create_terminal_quadrant, _create_confusion_matrix_quadrant,
# _create_status_quadrant, create_widgets, _update_clock, update_data) remain the same.

# [ ... _create_terminal_quadrant (unchanged) ... ]
def _create_terminal_quadrant(root, title, metric_key, row, col, fg_color="#2ECC71"):
    """Creates a generalized Terminal Output quadrant (Q1 and Q3)."""
    global metric_vars
    
    quadrant_frame = ttk.Frame(root, padding="15", relief="groove", borderwidth=1, style='Quad.TFrame')
    quadrant_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
    
    ttk.Label(quadrant_frame, text=title, font=("Helvetica", 14, "bold"), foreground="#2C3E50").pack(pady=(0, 5))
    
    terminal_text = tk.Text(
        quadrant_frame, bg="#2C3E50", fg=fg_color, insertbackground=fg_color,
        font=("Consolas", 10), state='disabled', wrap='word', relief='flat', borderwidth=0, padx=10, pady=10
    )
    terminal_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    metric_vars[metric_key] = {'widget': terminal_text}


# [ ... _create_confusion_matrix_quadrant (unchanged) ... ]
def _create_confusion_matrix_quadrant(root, title, metrics, row, col):
    """Creates the Machine Learning Confusion Matrix quadrant (Q2)."""
    global metric_vars, tp_label, fn_label, fp_label, tn_label
    global accuracy_var, precision_var, f1_score_var
    
    quadrant_frame = ttk.Frame(root, padding="15", relief="groove", borderwidth=1, style='Quad.TFrame')
    quadrant_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
    
    ttk.Label(quadrant_frame, text=title, font=("Helvetica", 14, "bold"), foreground="#2C3E50").pack(pady=(0, 10))

    matrix_frame = ttk.Frame(quadrant_frame, padding="10")
    matrix_frame.pack(pady=10)

    # Headers
    ttk.Label(matrix_frame, text="Predicted True", font=("Inter", 10, "bold"), foreground="#3498DB").grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(matrix_frame, text="Predicted False", font=("Inter", 10, "bold"), foreground="#3498DB").grid(row=0, column=2, padx=5, pady=5)
    ttk.Label(matrix_frame, text="Actual True", font=("Inter", 10, "bold"), foreground="#3498DB").grid(row=1, column=0, padx=5, pady=5)
    ttk.Label(matrix_frame, text="Actual False", font=("Inter", 10, "bold"), foreground="#3498DB").grid(row=2, column=0, padx=5, pady=5)
    
    matrix_position_map = {
        "True Positives (TP)": (1, 1), 
        "False Negatives (FN)": (1, 2),
        "False Positives (FP)": (2, 1),
        "True Negatives (TN)": (2, 2)  
    }
    
    for name, (r, c) in matrix_position_map.items():
        metric_var = tk.StringVar(root, value="0")
        label_widget = ttk.Label(matrix_frame, textvariable=metric_var, 
                                 font=("Inter", 16, "bold"), relief="raised", padding=5, width=8, anchor="center")
        label_widget.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        
        metric_vars[name] = {'var': metric_var, 'widget': label_widget}
        
        if name == "True Positives (TP)": tp_label = label_widget
        elif name == "False Negatives (FN)": fn_label = label_widget
        elif name == "False Positives (FP)": fp_label = label_widget
        elif name == "True Negatives (TN)": tn_label = label_widget

    # Derived Metrics Area
    derived_metrics_frame = ttk.Frame(quadrant_frame, padding="5")
    derived_metrics_frame.pack(fill='x', padx=10, pady=10)
    
    accuracy_var = tk.StringVar(root, value="---")
    precision_var = tk.StringVar(root, value="---")
    f1_score_var = tk.StringVar(root, value="---")
    
    ttk.Label(derived_metrics_frame, text="Accuracy:", font=("Inter", 10)).grid(row=0, column=0, sticky="w")
    ttk.Label(derived_metrics_frame, textvariable=accuracy_var, font=("Inter", 12, "bold"), foreground="#2980B9").grid(row=0, column=1, sticky="e")
    
    ttk.Label(derived_metrics_frame, text="Precision:", font=("Inter", 10)).grid(row=1, column=0, sticky="w")
    ttk.Label(derived_metrics_frame, textvariable=precision_var, font=("Inter", 12, "bold"), foreground="#2980B9").grid(row=1, column=1, sticky="e")

    ttk.Label(derived_metrics_frame, text="F1 Score:", font=("Inter", 10)).grid(row=2, column=0, sticky="w")
    ttk.Label(derived_metrics_frame, textvariable=f1_score_var, font=("Inter", 12, "bold"), foreground="#2980B9").grid(row=2, column=1, sticky="e")
    
    derived_metrics_frame.columnconfigure(1, weight=1)

#Creating 4 qudrants 
def _create_status_quadrant(root, row, col):
    """Creates the dedicated System Status quadrant (Q4)."""
    global time_var, status_var, last_update_var
    
    status_title = "Data updates"
    status_frame = ttk.Frame(root, padding="15", relief="groove", borderwidth=1, style='Quad.TFrame')
    status_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
    
    ttk.Label(status_frame, text=status_title, font=("Helvetica", 14, "bold"), foreground="#2C3E50").pack(pady=(0, 20))
    
    time_var = tk.StringVar(root, value="00:00:00")
    ttk.Label(status_frame, textvariable=time_var, font=("Digital-7", 48, "bold"), foreground="#3498DB").pack(pady=10)
    
    status_var = tk.StringVar(root, value="Awaiting external data...")
    ttk.Label(status_frame, textvariable=status_var, font=("Inter", 12, "italic"), foreground="#34495E").pack(pady=20)
    
    last_update_var = tk.StringVar(root, value="")
    ttk.Label(status_frame, textvariable=last_update_var, font=("Helvetica", 30, "bold"), foreground="#007DA3").pack(pady=50) #QQQ


#Confusion matrix
def create_widgets(root):
    """Sets up the visual layout of the dashboard."""
    style = ttk.Style(root)
    style.configure('Quad.TFrame', background='white', relief='raised', borderwidth=1, padding=10)
    
    _create_terminal_quadrant(root, "Current System State", "Terminal Output", 0, 0, fg_color="#2ECC71")
    _create_confusion_matrix_quadrant(root, "ML CONFUSION MATRIX", QUADRANT_GROUPS["CONFUSION MATRIX"], 0, 1)
    _create_terminal_quadrant(root, "Production line State", "Process Log Output", 1, 0, fg_color="#F1C40F")
    _create_status_quadrant(root, 1, 1)

#Updateing clock in Q4
def _update_clock(root):
    """Updates the System Status Quadrant (Q4) clock every second."""
    if not root_app.winfo_exists():
        global interupt
        interupt = True

    global time_var
    current_time = time.strftime('%H:%M:%S')
    time_var.set(current_time)

    # Schedule the next clock update (this is continuous)
    root.after(updateFreq, lambda: _update_clock(root))
##
# [ ... update_data (unchanged) ... ]
def update_data(root):
    """Performs a SINGLE update cycle using the data stored in current_dashboard_data."""
    global current_dashboard_data
    global tp_label, fn_label, fp_label, tn_label, fp_label, tn_label
    global accuracy_var, precision_var, f1_score_var
    global status_var, last_update_var

    current_data = current_dashboard_data
    
    # 1. Update Terminal Outputs (Q1 and Q3)
    for terminal_key in ["Terminal Output", "Process Log Output"]:
        terminal_output = current_data.get(terminal_key, "Log unavailable.")
        terminal_item = metric_vars.get(terminal_key)
        
        if terminal_item and 'widget' in terminal_item:
            text_widget = terminal_item['widget']
            text_widget.config(state='normal')
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', terminal_output)
            text_widget.see(tk.END) 
            text_widget.config(state='disabled')
    
    # 2. Update Confusion Matrix (Q2)
    tp = current_data.get("True Positives (TP)", 0)
    fp = current_data.get("False Positives (FP)", 0)
    tn = current_data.get("True Negatives (TN)", 0)
    fn = current_data.get("False Negatives (FN)", 0)
    
    for label in QUADRANT_GROUPS["CONFUSION MATRIX"]:
        if label in metric_vars:
            metric_vars[label]['var'].set(str(current_data.get(label, 0)))

    # 3. Calculate and Update Derived Scores (Q2)
    total_samples = tp + fp + tn + fn
    accuracy, precision, recall = 0.0, 0.0, 0.0
    
    if total_samples > 0:
        accuracy = (tp + tn) / total_samples
        accuracy_var.set(f"{accuracy * 100:.2f}%")
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        precision_var.set(f"{precision * 100:.2f}%" if precision > 0 else "N/A")
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        f1_score_var.set(f"{f1_score * 100:.2f}%" if f1_score > 0 else "N/A")
    else:
        accuracy_var.set("N/A")
        precision_var.set("N/A")
        f1_score_var.set("N/A")

    # 4. Apply Matrix Specific Styling
    if tp_label: tp_label.config(background=("#16A085" if tp > 80 else "#F39C12"), foreground="white")
    if fn_label: fn_label.config(background=("#E74C3C" if fn > 5 else "#F39C12" if fn > 1 else "#34495E"), foreground="white")
    if fp_label: fp_label.config(background="#F39C12", foreground="#2C3E50")
    if tn_label: tn_label.config(background="#ECF0F1", foreground="#2C3E50")

    # 5. Update System Status Message (Q4) and Last Update Time
    if accuracy < 0.95 and total_samples > 0:
        status_var.set("WARNING: ML Accuracy low or critical FN count. Review required.")
    else:
        status_var.set("OPERATIONAL - Awaiting new data.")
        
    #last_update_var.set(f"Data Last Updated: {updateTime}")
    # NO root.after() call here. The update is one-time only.

# ----------------------------------------------------------------------
# --- MAIN APPLICATION LOGIC (Modified) ---
# ----------------------------------------------------------------------

def run_dashboard():
    """Initializes and runs the Tkinter dashboard."""
    global root_app
    
    # 1. Initialize the root window
    root = tk.Tk()
    root_app = root 
    root.title("ML-Integrated Assembly Line Monitor (External Control)")
    root.geometry("800x600") 
    root.config(bg="#FFFFFF")
    
    # 2. Configure grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    
    # 3. Create widgets
    create_widgets(root)
    
    # 4. Start the ONLY continuous loops: the clock and the queue poller
    _update_clock(root)
    # Start the queue polling mechanism
    _check_queue(root) 
    
    # 5. Perform the initial data update (by placing it in the queue)
    #set_and_update_data(initializationData)
    if root_app and root_app.winfo_exists():
        # Place the new data onto the queue. This is safe to call from any thread.
        #uptateTime = time.strftime('%H:%M:%S')
        data_queue.put(initializationData)
    
    # 6. Start the Tkinter event loop
    root.mainloop()









