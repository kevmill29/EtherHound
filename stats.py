import sqlite3

conn = sqlite3.connect('probe_log.db')
cursor = conn.cursor()

print("\n-  Probe Request Statistics  -\n")




#Total captures
cursor.execute("SELECT COUNT(*) FROM probe_requests")
print(f"Total probes captured:  {cursor.fetchone()[0]}")

#Unique devices
cursor.execute("SELECT COUTN(DISTINCT mac_address) FROM probe_requests")
print(f"Unique devices seen:    {cursor.fetchone()[0]}")

#Randomized Vs Real MACS

cursor.execute("SELECT COUNT(*) FROM probe_requests WHERE randomized = 1")
print(f"Randomized MACS:        {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM probe_requests WHERE randomized = 0")
print(f"Real MACS:            {cursor.fetchone()[0]}")

#Top Vendors
print("\nTop  5 Vendors seen:")
cursor.execute('''
        SELECT vendor, COUNT(*) as total
        FROM probe_requests
        GROUP BY vendor
        ORDER BY total DESC LIMIT 5
        ''')
for row in cursor.fetchall():
        print(f"   {row[0]} ({row[1]}) -> {row[2]} probes")

conn.close()


#Top most active devices
print("\nTop 5 Most Active Devices:")
cursor.execute('''
        SELECT mac_address, vendor, COUNT(*) as total
        FROM probe_requests
        GROUP BY mac_address,
        ORDER BY total DESC LIMIT 5
        ''')
for row in cursor.fetchall():
        print(f"   {row[0]} ({row[1]}) -> {row[2]} probes")

conn.close()
