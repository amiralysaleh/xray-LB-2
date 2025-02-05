import requests
import json
import jdatetime
import base64
import re
import random
import pytz
from datetime import datetime

MAX_CONFIGS = 60

def is_base64(s):
    # Check if string matches base64 pattern
    pattern = r'^[A-Za-z0-9+/]*={0,2}$'
    return bool(re.match(pattern, s)) and len(s) % 4 == 0

def decode_base64_content(content):
    try:
        if is_base64(content):
            decoded = base64.b64decode(content).decode('utf-8')
            # Split decoded content into lines and filter empty lines
            return [line for line in decoded.split('\n') if line.strip()]
        return [content]  # Return as single-item list if not base64
    except:
        return [content]  # Return original content if decoding fails

def get_raw_configs():
    url = "https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_RAW.txt"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            content = response.text.strip()
            
            # First, try to decode the entire content if it's base64
            all_configs = []
            if is_base64(content):
                print("Detected base64 encoded content, decoding...")
                all_configs = decode_base64_content(content)
            else:
                # If not base64, split by lines and try each line
                lines = content.split('\n')
                for line in lines:
                    decoded_lines = decode_base64_content(line.strip())
                    all_configs.extend(decoded_lines)
            
            print(f"Total configs after decoding: {len(all_configs)}")
            
            # Apply the limit after decoding
            if len(all_configs) > MAX_CONFIGS:
                all_configs = random.sample(all_configs, MAX_CONFIGS)
                print(f"Limited to {MAX_CONFIGS} random configs")
            
            return all_configs
            
        print(f"Failed to get configs. Status code: {response.status_code}")
        return []
    except Exception as e:
        print(f"Error getting configs: {str(e)}")
        return []

def process_configs():
    configs = get_raw_configs()
    if not configs:
        print("No configs found!")
        return
    
    print(f"Processing {len(configs)} configs")
    
    try:
        url = "https://surfboardv2ray.pythonanywhere.com/convert"
        
        # Prepare JSON payload
        payload = {
            "config": "\n".join(configs)
        }
        
        # Headers for JSON request
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Send POST request with JSON data
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                # Parse the JSON string from result
                config_json = json.loads(result['result'])
                
                # Get current Tehran time and convert to Persian date
                tehran_tz = pytz.timezone('Asia/Tehran')
                tehran_time = datetime.now(tehran_tz)
                persian_date = jdatetime.datetime.fromgregorian(
                    datetime=tehran_time
                )
                persian_datetime = persian_date.strftime("%Y-%m-%d %H:%M")
                
                # Update the remarks
                config_json['remarks'] = f"𓅃 | ({persian_datetime})"
                
                # Convert back to formatted JSON string
                formatted_json = json.dumps(config_json, ensure_ascii=False, indent=2)
                
                # Save the result
                with open('v2ray_processed.txt', 'w', encoding='utf-8') as f:
                    f.write(formatted_json)
                print("Successfully saved processed configs with Tehran time")
            else:
                print("Error: Response does not contain 'result' field")
                print(f"Response content: {result}")
        else:
            print(f"Error: Server returned status code {response.status_code}")
            print(f"Response content: {response.text}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Full error details: ", e)

if __name__ == "__main__":
    process_configs()
