import os
from pythonping import ping
import time
import threading
from dotenv import load_dotenv
from wakeonlan import send_magic_packet

# Load ENV file
load_dotenv()

# Create lists with variables found in the .env file
host_ips = os.environ.get('ip_list').split(",")
host_macs = os.environ.get('mac_list').split(",")


# Function to perform ping and respond with result
def ping_host(host):
    result = str(ping(f'{host}', count=1)).lower()
    if "timed out" in result or "100% packet loss" in result \
            or "host unreachable" in result:
        return "NOT CONNECTED"
    return "CONNECTED"


# Function to send magic packet if ping fails
def wake(ip_addr, mac_addr):
    while True:
        fail_counter = 0
        while fail_counter < 3:
            send_ping = ping_host(ip_addr)
            print(f"(Attempt {fail_counter + 1}) for host: {ip_addr}")
            if send_ping == "NOT CONNECTED":
                print(f"Unable to ping: {ip_addr}")
                print("Retrying in 20 seconds...\n")
                time.sleep(20)
                fail_counter = fail_counter + 1
            if send_ping == "CONNECTED":
                print(f"Ping was successful for: {ip_addr}")
                print(f"Host is now online...")
                print(f"Waiting 10 minutes before pinging {ip_addr} again...\n")
                time.sleep(600)
            if fail_counter == 3:
                clean_mac = mac_addr.replace(":", "").replace("-", "").replace(".", "")
                mac = ".".join(clean_mac[x:x + 2] for x in range(0, len(clean_mac), 2))
                send_magic_packet(mac)
                print(f"Ping failed {fail_counter} times for host: {ip_addr}.\nAttempting to send magic packet.")
                print(f"Sent magic packet to: (IP: {ip_addr} , MAC: {mac})")
                print(f"Waiting for 60 seconds before pinging {ip_addr} again...\n")
                time.sleep(60)


# Make individual threads for each ip/mac for simultaneous processing
for (ips, macs) in zip(host_ips, host_macs):
    threading.Thread(target=wake, args=(ips, macs,)).start()
