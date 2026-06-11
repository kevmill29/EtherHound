from scapy.all import sniff, Dot11ProbeReq
from datetime import datetime
from mac_vendor_lookup import MacLookup, VendorNotFoundError
import sqlite3
import threading
import subprocess
import time

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
        id INTEGER PRIMARY KEY AUTOINCREMENT
        timestamp TEXT,
        mac_address TEXT,
        ssid TEXT
        )
        ''')
    conn.commit()
    conn.close()


#2nd Step --- Log to Database ---

def log_to_db(timestamp, mac, ssid):
    conn = sqlite3.connect("probe_log.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO probe_requests (timestamp, mac_address, ssid)
