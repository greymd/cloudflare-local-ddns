import requests
import subprocess
import yaml

def load_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_local_ip(interface):
    try:
        result = subprocess.run(['ip', 'addr', 'show', interface], capture_output=True, text=True)
        output = result.stdout
        ip_line = [line for line in output.split('\n') if 'inet ' in line]
        if ip_line:
            ip_address = ip_line[0].split()[1].split('/')[0]
            return ip_address
        else:
            raise Exception(f"No IP address found for {interface}")
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return None

def get_zone_id(api_token, zone_name):
    url = f"https://api.cloudflare.com/client/v4/zones?name={zone_name}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        zone_id = response.json()['result'][0]['id']
        return zone_id
    else:
        print(f"Error fetching zone ID: {response.status_code}")
        return None

def get_record_id(api_token, zone_id, record_name):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json()['result']
        if records:
            return records[0]['id']
        else:
            print("No A record found")
            return None
    else:
        print(f"Error fetching record ID: {response.status_code}")
        return None

def update_record(api_token, zone_id, record_id, ip_address, record_name):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": record_name,
        "content": ip_address,
        "ttl": 60
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Record updated successfully")
    else:
        print(f"Error updating record: {response.status_code}")

def main():
    config = load_config()
    api_token = config['cloudflare']['api_token']
    zone_name = config['cloudflare']['zone_name']
    record_name = config['cloudflare']['record_name']
    interface = config['network']['interface']
    local_ip = get_local_ip(interface)
    if local_ip:
        print(f"Local IP: {local_ip}")
        zone_id = get_zone_id(api_token, zone_name)
        if zone_id:
            record_id = get_record_id(api_token, zone_id, record_name)
            if record_id:
                update_record(api_token, zone_id, record_id, local_ip, record_name)

if __name__ == "__main__":
    main()
