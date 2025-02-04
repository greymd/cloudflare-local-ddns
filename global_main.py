from utils import *

def get_global_ip():
    url = f"https://checkip.amazonaws.com"
    headers = {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        global_ip = response.text
        return global_ip
    else:
        print(f"Error fetching global IP: {response.status_code}")
        return None

def main():
    config = load_config('global_config.yaml')
    cache_file = 'global_ip_cache.txt'
    api_token = config['cloudflare']['api_token']
    zone_name = config['cloudflare']['zone_name']
    record_names = config['cloudflare']['record_names']

    global_ip = get_global_ip()
    if global_ip:
        cached_ip = read_cached_ip(cache_file)
        if cached_ip == global_ip:
            print(f"Global IP has not changed: {global_ip}")
            return

        print(f"Global IP: {global_ip}")
        zone_id = get_zone_id(api_token, zone_name)
        if zone_id:
            for record_name in record_names:
                record_id = get_record_id(api_token, zone_id, record_name)
                if record_id:
                    if update_record(api_token, zone_id, record_id, global_ip, record_name):
                        write_cached_ip(global_ip, cache_file)

if __name__ == "__main__":
    main()
