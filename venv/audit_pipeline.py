import os
from netmiko import ConnectHandler

# da 4 IOU switches on the VLAN 20 MGT subnet
switches = [
    {"device_type": "cisco_ios", "host": "10.0.20.11", "username": "admin", "password": "cisco123"},
    {"device_type": "cisco_ios", "host": "10.0.20.12", "username": "admin", "password": "cisco123"},
    {"device_type": "cisco_ios", "host": "10.0.20.13", "username": "admin", "password": "cisco123"},
    {"device_type": "cisco_ios", "host": "10.0.20.14", "username": "admin", "password": "cisco123"},
]

backup_dir = "telemetry_backups"
os.makedirs(backup_dir, exist_ok=True)

for switch in switches:
    print(f"Establishing SSH connection to {switch['host']}...")
    try:
        net_connect = ConnectHandler(**switch)
        hostname = net_connect.find_prompt().strip("#")
        print(f"[{hostname}] Connected! Pulling running config...")
        
        config_output = net_connect.send_command("show run")
        
        file_path = os.path.join(backup_dir, f"{hostname}_running_config.txt")
        with open(file_path, "w") as f:
            f.write(config_output)
            
        net_connect.disconnect()
        print(f"[{hostname}] ✅ Telemetry saved to {file_path}\n")
        
    except Exception as e:
        print(f"❌ Connection failed for {switch['host']}: {e}\n")