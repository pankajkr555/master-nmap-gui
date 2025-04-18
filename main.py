import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import time

# List of available scans and corresponding commands
SCANS = {
    "Ping Scan": "-sn",
    "ARP Ping Scan": "-sn -PR",
    "UDP Ping Scan": "-sn -PU",
    "ICMP Echo Ping Scan": "-sn -PE",
    "ICMP Address Mask Ping Scan": "-sn -PM",
    "TCP SYN Ping Scan": "-sn -PS",
    "TCP ACK Ping Scan": "-sn -PA",
    "IP Protocol Ping Scan": "-sn -PO",
    "TCP Connect Scan": "-sT -v",
    "Stealth SYN Scan": "-sS -v",
    "Xmas Scan": "-sX -v",

    "ACK Scan": "-sA -v",
    "UDP Scan": "-sU -v",
    "Aggressive Full Scan": "-T4 -A -v",
    "List Scan": "-sL -v",
    "SCTP INIT Scan": "-sY -v",
    "SCTP COOKIE ECHO Scan": "-sZ -v",
    "OS Detection": "-O",
    "Service Version Detection": "-sV",
    "Aggressive Scan": "-A",
    "UDP Scan (Top 10)": "-sU --top-ports 10",
    "Top 1000 TCP Ports": "--top-ports 1000",
    "Vulnerability Scan": "--script vuln"
}

# Function to convert XML to JSON
def convert_xml_to_json(xml_file_path, json_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        def xml_to_dict(elem):
            result = {}
            if elem.text and elem.text.strip():
                result["text"] = elem.text.strip()
            for key, val in elem.attrib.items():
                result[f"@{key}"] = val
            for child in elem:
                child_result = xml_to_dict(child)
                if child.tag not in result:
                    result[child.tag] = child_result
                else:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_result)
            return result

        data_dict = {root.tag: xml_to_dict(root)}

        with open(json_file_path, 'w') as jf:
            json.dump(data_dict, jf, indent=4)

    except Exception as e:
        with open(json_file_path, 'w') as jf:
            json.dump({"error": str(e)}, jf)

# Function to run a single Nmap command and return outputs in XML, JSON, and plain text
def run_nmap(command, output_base):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xml_path = f"{output_base}_{timestamp}.xml"
        json_path = f"{output_base}_{timestamp}.json"
        txt_path = f"{output_base}_{timestamp}.txt"

        # XML Output
        xml_command = f"{command} -oX {xml_path}"
        subprocess.run(xml_command, shell=True, capture_output=True, text=True)

        # Convert XML to JSON
        convert_xml_to_json(xml_path, json_path)

        # Plain Text Output
        txt_command = f"{command} -oN {txt_path}"
        subprocess.run(txt_command, shell=True, capture_output=True, text=True)

        return xml_path, txt_path, json_path
    except Exception as e:
        return None, None, None

# Function to update progress bar
def update_progress(progress, total, bar, status_label):
    percent = int((progress / total) * 100)
    bar["value"] = percent
    status_label.config(text=f"Progress: {percent}%")

# Hacker-style animation

def hacker_animation(texts, label):
    def animate():
        label.config(text="")
        for line in texts:
            for i in range(len(line) + 1):
                label.config(text="» " + line[:i])
                time.sleep(0.05)
            time.sleep(0.3)
    threading.Thread(target=animate).start()

# Function to run selected scans
def run_selected_scans(target, selected_scans, tab_control, progress_bar, status_label):
    total = len(selected_scans)
    progress = 0

    output_folder = os.path.join(os.getcwd(), "scan_outputs")
    os.makedirs(output_folder, exist_ok=True)

    for scan_name in selected_scans:
        base_cmd = f"nmap {SCANS[scan_name]} {target}"
        xml_file, txt_file, json_file = run_nmap(base_cmd, os.path.join(output_folder, scan_name.replace(' ', '_')))

        if txt_file:
            try:
                with open(txt_file, 'r') as f:
                    result_txt = f.read()
            except:
                result_txt = "Failed to read plain text output file."
        else:
            result_txt = "Error executing scan."

        if xml_file:
            try:
                with open(xml_file, 'r') as f:
                    result_xml = f.read()
            except:
                result_xml = "Failed to read XML output file."
        else:
            result_xml = "Error reading XML file."

        if json_file:
            try:
                with open(json_file, 'r') as f:
                    result_json = f.read()
            except:
                result_json = "Failed to read JSON output file."
        else:
            result_json = "Error reading JSON file."

        tab = tk.Frame(tab_control, bg="#1a1a1a")
        tab_control.add(tab, text=scan_name)

        # Text Output Area
        output_area_txt = scrolledtext.ScrolledText(tab, font=("Consolas", 10), bg="#0f0f0f", fg="lime", height=10)
        output_area_txt.pack(fill='both', expand=True)
        output_area_txt.insert(tk.END, f"Command: {base_cmd}\n")
        output_area_txt.insert(tk.END, f"TXT Output: {txt_file}\n\n")
        output_area_txt.insert(tk.END, result_txt)

        # XML Output Area
        output_area_xml = scrolledtext.ScrolledText(tab, font=("Consolas", 10), bg="#1a1a1a", fg="cyan", height=10)
        output_area_xml.pack(fill='both', expand=True)
        output_area_xml.insert(tk.END, f"XML Output: {xml_file}\n\n")
        output_area_xml.insert(tk.END, result_xml)

        # JSON Output Area
        output_area_json = scrolledtext.ScrolledText(tab, font=("Consolas", 10), bg="#1a1a1a", fg="orange", height=10)
        output_area_json.pack(fill='both', expand=True)
        output_area_json.insert(tk.END, f"JSON Output: {json_file}\n\n")
        output_area_json.insert(tk.END, result_json)

        progress += 1
        update_progress(progress, total, progress_bar, status_label)

# GUI Design
def launch_gui():
    window = tk.Tk()
    window.title("Master Nmap")
    window.configure(bg="#0f0f0f")
    window.geometry("1000x700")

    tk.Label(window, text="Target IP or Domain:", bg="#0f0f0f", fg="lime", font=("Consolas", 12)).pack(pady=5)
    target_entry = tk.Entry(window, font=("Consolas", 14), width=50, bg="#1f1f1f", fg="white", insertbackground="white")
    target_entry.pack(pady=5)

    scan_frame = tk.Frame(window, bg="#0f0f0f")
    scan_frame.pack(pady=5)

    check_vars = {}
    for scan in SCANS:
        var = tk.IntVar()
        chk = tk.Checkbutton(scan_frame, text=scan, variable=var, bg="#0f0f0f", fg="lime", font=("Consolas", 10), selectcolor="#1f1f1f", activebackground="#0f0f0f")
        chk.pack(anchor='w')
        check_vars[scan] = var

    progress_bar = ttk.Progressbar(window, length=600)
    progress_bar.pack(pady=5)

    status_label = tk.Label(window, text="Progress: 0%", bg="#0f0f0f", fg="lime", font=("Consolas", 10))
    status_label.pack(pady=2)

    animation_label = tk.Label(window, text="", bg="#0f0f0f", fg="cyan", font=("Consolas", 12))
    animation_label.pack(pady=2)

    tab_control = ttk.Notebook(window)
    tab_control.pack(expand=1, fill='both')

    def on_scan():
        target = target_entry.get()
        if not target:
            status_label.config(text="Please enter a valid target.")
            return

        selected_scans = [scan for scan, var in check_vars.items() if var.get() == 1]
        if not selected_scans:
            status_label.config(text="Select at least one scan type.")
            return

        for tab in tab_control.tabs():
            tab_control.forget(tab)

        progress_bar["value"] = 0

        hacker_texts = ["Accessing Target...", "Initializing Recon Engine...", "Deploying Probes..."]
        hacker_animation(hacker_texts, animation_label)

        threading.Thread(target=run_selected_scans, args=(target, selected_scans, tab_control, progress_bar, status_label)).start()

    tk.Button(window, text="Start Scan", command=on_scan, font=("Consolas", 12), bg="lime", fg="black", width=20).pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    launch_gui()
