import requests
import json
import jdatetime

def get_raw_configs():
    url = "https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/V2RAY_RAW.txt"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text.strip().split('\n')
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
    
    print(f"Found {len(configs)} configs")
    
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
                
                # Get current Persian date and time
                now = jdatetime.datetime.now()
                persian_datetime = now.strftime("%Y-%m-%d %H:%M")
                
                # Update the remarks
                config_json['remarks'] = f"Xray-LB ({persian_datetime})"
                
                # Convert back to formatted JSON string
                formatted_json = json.dumps(config_json, ensure_ascii=False, indent=2)
                
                # Save the result
                with open('v2ray_processed.txt', 'w', encoding='utf-8') as f:
                    f.write(formatted_json)
                print("Successfully saved processed configs with Persian datetime")
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
