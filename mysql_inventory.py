import re
import mysql.connector
from netmiko import ConnectHandler

# Connect to Local MySQL 
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="p_ass",  
    database="netdevops_lab"
)
cursor = db_connection.cursor()

#  Define Network Inv
switches = [
    {"device_type": "cisco_ios", "host": "10.0.20.11", "username": "admin", "password": "p_ass"},
    {"device_type": "cisco_ios", "host": "10.0.20.12", "username": "admin", "password": "p_ass"},
    {"device_type": "cisco_ios", "host": "10.0.20.13", "username": "admin", "password": "p_ass"},
    {"device_type": "cisco_ios", "host": "10.0.20.14", "username": "admin", "password": "p_ass"},
]

print("Starting Network Telemetry Extraction...\n")

# Extract and Inject Data
for switch in switches:
    try:
        net_connect = ConnectHandler(**switch)
        hostname = net_connect.find_prompt().strip("#")
        print(f"[{hostname}] Connected! Parsing telemetry...")
        
        # Pull raw outputs
        sh_ver = net_connect.send_command("show version")
        sh_int = net_connect.send_command("show interfaces Ethernet0/0")
        
        # Regex Parsing Logic
        os_match = re.search(r"Version (\d+\.\d+[A-Za-z0-9\(\)\.]+)", sh_ver)
        os_version = os_match.group(1) if os_match else "Unknown"
        
        img_match = re.search(r"System image file is \"(.+?)\"", sh_ver)
        system_image = img_match.group(1) if img_match else "Unknown"
        
        uptime_match = re.search(r"uptime is (.+)", sh_ver)
        uptime = uptime_match.group(1) if uptime_match else "Unknown"
        
        mac_match = re.search(r"address is ([0-9a-fA-F\.]+)", sh_int)
        base_mac = mac_match.group(1) if mac_match else "Unknown"
        
        sn_match = re.search(r"Processor board ID (\S+)", sh_ver)
        serial_number = sn_match.group(1) if sn_match else "IOU-VIRTUAL-SN"
        
        reg_match = re.search(r"Configuration register is (\S+)", sh_ver)
        config_register = reg_match.group(1) if reg_match else "Unknown"
        
        # SQL Injection
        sql = """
            INSERT INTO hardware_inventory 
            (hostname, management_ip, vendor, platform_model, os_version, system_image, serial_number, uptime, config_register, base_mac_address) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (hostname, switch["host"], "Cisco", "IOU L2 Switch", os_version, system_image, serial_number, uptime, config_register, base_mac)
        
        cursor.execute(sql, values)
        db_connection.commit()  # Save changes to the database
        
        net_connect.disconnect()
        print(f"[{hostname}] ✅ Data successfully committed to MySQL!\n")
        
    except Exception as e:
        print(f"❌ Connection or Database failure for {switch['host']}: {e}\n")

# Clean up database conn
cursor.close()
db_connection.close()
print("Pipeline Complete.")