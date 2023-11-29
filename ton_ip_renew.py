import requests
import time
import os
import json
import socket
import struct

def get_external_ip():
    response = requests.get('https://httpbin.org/ip')
    ip_dotted = response.json()['origin']
    # Convert dotted IP to decimal
    ip_decimal = struct.unpack('!L', socket.inet_aton(ip_dotted))[0]
    return ip_decimal

def read_last_ip():
    try:
        with open('/var/ton-work/db/last_ip.txt', 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None

def write_last_ip(ip):
    with open('/var/ton-work/db/last_ip.txt', 'w') as file:
        file.write(str(ip))

def update_config_and_restart_service(new_ip):
    config_path = '/var/ton-work/db/config.json'
    with open(config_path, 'r+') as file:
        config = json.load(file)

        # Assuming there's only one address block to update
        if config['addrs'][0]['ip'] != new_ip:
            config['addrs'][0]['ip'] = new_ip

            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()
    
    os.system('systemctl restart your_service_name')

def main():
    while True:
        current_ip = get_external_ip()
        last_ip = read_last_ip()

        if current_ip != last_ip:
            update_config_and_restart_service(current_ip)
            write_last_ip(current_ip)
        
        time.sleep(1800) # Wait for 30 minutes

if __name__ == "__main__":
    main()
