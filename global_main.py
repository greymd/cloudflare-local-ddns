from utils import *

def main():
    config = load_config('global_config.yaml')
    api_token = config['cloudflare']['api_token']
    zone_name = config['cloudflare']['zone_name']
    record_names = config['cloudflare']['record_names']
    interface = config['network']['interface']

    local_ip = get_local_ip(interface)
    if local_ip:
        cached_ip = read_cached_ip()
        if cached_ip == local_ip:
            print(f"Global IP has not changed: {local_ip}")
            return

        print(f"Global IP: {local_ip}")
        zone_id = get_zone_id(api_token, zone_name)
        if zone_id:
            for record_name in record_names:
                record_id = get_record_id(api_token, zone_id, record_name)
                if record_id:
                    if update_record(api_token, zone_id, record_id, local_ip, record_name):
                        write_cached_ip(local_ip)

if __name__ == "__main__":
    main()
