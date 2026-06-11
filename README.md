# EtherHound
A passive WiFi probe request logger with MAC vendor lookup,  randomized MAC detection, channel hopping, and Folium map visualization.

EtherHound is intended for **educational purposes only**.

- Only use this tool on networks you own or have **explicit written permission** to monitor
- The author is not responsible for any misuse or damage caused by this tool
- Laws regarding packet capture vary by country and jurisdiction
- Unauthorized network monitoring may violate local laws

- ## Features
- Passive WiFi probe request capture
- MAC vendor identification
- Randomized MAC detection
- Channel hopping across 2.4GHz and 5GHz
- SQLite logging
- Interactive Folium map generation

## Requirements
- Linux (Arch or Kali recommended)
- WiFi adapter that supports monitor mode
- Python 3

## Installation
```bash
git clone https://github.com/yourusername/etherhound
cd etherhound
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
# Put adapter in monitor mode
sudo airmon-ng start wlan0 (replace with your interface name)

# Run the sniffer
sudo python3 probe_logger.py

# Generate map
python3 map_generator.py

# View stats
python3 stats.py
```

## ⚠️ Legal Disclaimer
This tool is for educational purposes only. 
Only use on networks you own or have explicit permission to monitor.
