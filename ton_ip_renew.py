import requests
import time
import os
import json
import socket
import struct
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_external_ip():
    response = requests.get('https://httpbin.org/ip')
    ip_dotted = response.json()['origin']
    # Convert dotted IP to decimal
    ip_decimal = struct.unpack('!L', socket.inet_aton(ip_dotted))[0]
    return ip_decimal

def read_last_ip():
    try:
        with open('last_ip.txt', 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None

def write_last_ip(ip):
    with open('last_ip.txt', 'w') as file:
        file.write(str(ip))

def update_config_and_restart_service(new_ip):
    config_path = '/var/ton-work/db/config.json'
    with open(config_path, 'r+') as file:
        config = json.load(file)

        if config['addrs'][0]['ip'] != new_ip:
            config['addrs'][0]['ip'] = new_ip

            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()
    
    os.system('systemctl restart validator.service')
    os.system('systemctl restart mytoncore.service')

def main():
    while True:
        current_ip = get_external_ip()
        dotted_ip = socket.inet_ntoa(struct.pack('!L', current_ip))
        print(f'[{get_timestamp()}] Current IP (Decimal): {current_ip}')
        print(f'[{get_timestamp()}] Current IP (Dotted): {dotted_ip}')
        
        last_ip = read_last_ip()
        last_ip_dotted = socket.inet_ntoa(struct.pack('!L', last_ip))
        print(f'[{get_timestamp()}] Last IP: {last_ip}')
        print(f'[{get_timestamp()}] Last IP (Dotted): {last_ip_dotted}')

        if current_ip != last_ip:
            print(f'[{get_timestamp()}] IP changed. Updating config and restarting services.')
            update_config_and_restart_service(current_ip)
            write_last_ip(current_ip)
        else:
            print(f'[{get_timestamp()}] No change in IP.')

        time.sleep(1800)  # Wait for 30 minutes

if __name__ == "__main__":
    main()
