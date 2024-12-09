import streamlit as st
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
from queue import Queue
import detection
import audio
import head_pose

# Global variables for real-time graph and control
PLOT_LENGTH = 200
XDATA = list(range(PLOT_LENGTH))
YDATA = [0] * PLOT_LENGTH
data_queue = Queue()
stop_flag = threading.Event()

# Function to simulate the detection graph update
def run_detection():
    global YDATA
    while not stop_flag.is_set():
        detection.process()  # Update the cheat percentage
        data_queue.put(detection.PERCENTAGE_CHEAT)
        time.sleep(0.2)  # Match the detection frequency

# Function to start head pose and audio detection in threads
def start_background_processes():
    stop_flag.clear()  # Reset the stop flag
    head_pose_thread = threading.Thread(target=head_pose.pose, daemon=True)
    audio_thread = threading.Thread(target=audio.sound, daemon=True)
    detection_thread = threading.Thread(target=run_detection, daemon=True)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()

    return [head_pose_thread, audio_thread, detection_thread]

# Streamlit app starts here
def main():
    st.set_page_config(page_title="Suspicious Behavior Detection", layout="wide")
    st.title("AI Proctoring Dashboard")

    # Real-time detection graph
    st.subheader("Real-Time Suspicious Behavior Detection")
    graph_placeholder = st.empty()

    # Instructions
    st.sidebar.title("Instructions")
    st.sidebar.write("This application monitors suspicious behavior based on head pose and audio activity in real time.")
    st.sidebar.write("1. Ensure your webcam and microphone are accessible.")
    st.sidebar.write("2. Use the Start/Stop buttons to control the detection process.")
    st.sidebar.write("3. Check the graph for suspicious behavior (Cheat probability > 60%).")

    # Control Panel
    st.sidebar.subheader("Control Panel")
    start_button = st.sidebar.button("Start Detection")
    stop_button = st.sidebar.button("Stop Detection")

    # Initialize thread container
    threads = []

    if start_button:
        st.sidebar.write("Detection started. Monitoring real-time data...")
        threads = start_background_processes()

    if stop_button:
        stop_flag.set()  # Set the stop flag
        st.sidebar.write("Detection stopped. Processes will terminate.")
        for thread in threads:
            thread.join(timeout=1)  # Allow threads to terminate gracefully

    # Real-time graph update loop
    chart = st.line_chart(YDATA)

    while True:
        if not data_queue.empty():
            new_value = data_queue.get()
            YDATA.pop(0)
            YDATA.append(new_value)
            chart.line_chart(YDATA)
        if stop_flag.is_set():
            break  # Exit the graph update loop when stopped
        time.sleep(0.1)  # Refresh rate for UI updates


if __name__ == "__main__":
    main()
