from scapy.all import sniff, Dot11ProbeReq
from datetime import datetime
from mac_vendor_lookup import MacLookup, VendorNotFoundError
import sqlite3
import threading
import subprocess
import time
import os
import socket
import pynmea2


#clean up function
def archive_old_database():
    db_filename = "probe_log.db"
    
    # Check if the database file from a previous run exists
    if os.path.exists(db_filename):
        # Create a unique name using the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"probe_log_archive_{timestamp}.db"
        
        # Rename (move) the file
        os.rename(db_filename, archive_name)
        print(f"[*] Saved previous session data to: {archive_name}")

#get latitude and longitude from phone via tethering
def get_gps_from_phone():
    #replace with you phone's IP address and app port
    #I  will be using an app called GPS2IP to get info
    PHONE_IP = "192.168.1.100"  # Replace with your phone's IP
    PHONE_PORT = 8080  # Replace with your app's port

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0) # Don't freeze the script if phone disconnects
        sock.connect((PHONE_IP, PHONE_PORT))
        data = sock.recv(1024).decode('ascii', errors='ignore')
        sock.close()

        #parse the raw data to find the latitude and longitude
        for line in data.split('\n'):
            if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                msg = pynmaea2.parse(line)
                if msg.latitude != 0.0
                    return msg.latitude, msg.longitude

    except Exception as e:
        #Fail silently so sniffer doesn't crash
        pass
    
    return None, None #Return none if no valid GPS data is found

    


#-- Channels to hop accross 2.4ghz/5ghz --
CHANNELS_2GHZ = list(range(1,14))
CHANNELS_5GHZ = [36,40,44,48,52,56,60,64,100,149, 153,157,161]
ALL_CHANNELS = CHANNELS_2GHZ + CHANNELS_5GHZ

#--Channel Hopper--
def channel_hopper(interface, hop_interval=0.5):
    print(f"[*] Channel Hopper started on {interface}")
    while True:
        for channel in ALL_CHANNELS:
            try:
                subprocess.call(
                    ['iw', 'dev',  interface, 'set', 'channel', str(channel)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(hop_interval)

            except Exception as e:
                    print(f"[!] Channel  hop error: {e}")

#1st step  -- Database Setup --
def init_db():


    conn = sqlite3.connect("probe_log.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS probe_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        capture_time TEXT,
        vendor TEXT,
        mac TEXT,
        ssid TEXT,
        channel INTEGER,
        randomized INTEGER,
        latitude REAL,
        longitude REAL
        )
        ''')
    conn.commit()
    conn.close()


#2nd Step --- Log to Database ---

def log_to_db(capture_time, mac, ssid, vendor, randomized,channel, lat, lon):
    conn = sqlite3.connect("probe_log.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO probe_requests (capture_time, mac, ssid, vendor, randomized, channel, latitude, longitude)
        VALUES(?,?,?,?,?,?,?,?)
        ''', (capture_time, mac, ssid, vendor, randomized, channel, lat, lon))
    conn.commit()
    conn.close()    


#3rd Step --- MAC Address Lookup ---
def get_vendor(mac_address):
    try:
        return MacLookup().lookup(mac_address)
    except VendorNotFoundError:
        return "Unknown Vendor"
    except Exception:
        return "Lookup Error"


#4th Step Randomized MAC Check ---
def is_randomized(mac_address):
    first_octet=int(mac_address.split(':')[0], 16)
    return bool(first_octet & 0x02)


#5th  Step -- Get Current Channel--
def get_current_channel(interface):
    try:
        output = subprocess.check_output(
            ['iw', 'dev', interface, 'info'],
            stderr=subprocess.DEVNULL
        ).decode()
        for line in output.split('\n'):
            if 'channel' in line:
                return(int(line.strip('.').split()[1]))
    except Exception:
        return None


#6th Step -- Packet Handler--
def handle_packet(pkt):
    mac= "";
    if pkt.haslayer(Dot11ProbeReq):
        mac = pkt.addr2
        #error handling for no mac address
        if not mac:
            return

        ssid=pkt.info.decode(errors='ignore')  if pkt.info else "<wildcard>"
        capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vendor = get_vendor(mac)
        randomized= is_randomized(mac)
        randomized_str="Yes" if randomized else "No"
        channel = get_current_channel(INTERFACE)
        log_to_db(capture_time, mac, ssid, vendor, randomized, channel, LAT, LON) #Hardcoded coordinates for now, will find out later how to prompt user for them

        #print to console
        print(f"[{capture_time}]")
        print(f"MAC:    {mac}")
        print(f"SSID:   {ssid}")
        print(f"Vendor: {vendor}")
        print(f"Random MAC: {randomized_str}")
        print(f"Channel: {channel}")
        print("-" * 40)


#MAIN

#replace this with your interface name(run ip link to see available interfaces)

#INTERFACE = "wlan0"
#Set your current location coordinates here
#Use google maps to copy coordinates
#Note- Since a heatmap visualizes density, hardcoded coordinates 
#will just look like one giant, intensely glowing red dot until you hook up your actual GPS module

#LAT=0.0
#LON=0.0
INTERFACE = "wlp6s0mon"
LAT = -74.02064671427073
LON = 41.4894760813576

#clean up first then init
archive_old_database()

init_db()

print("[*] Updating MAC vendor database...")
MacLookup().update_vendors()

#Start channel hopping in a seperate thread
hopper_thread = threading.Thread(
    target=channel_hopper,
    args=(INTERFACE,),
    daemon= True #will kill automatically when the main program exits
)
hopper_thread.start()

print("[*] Starting probe sniffer.. Press CTRL+C to stop.\n")
sniff(iface=INTERFACE, prn=handle_packet, store=False)