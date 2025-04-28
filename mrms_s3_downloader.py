import os
import requests
from datetime import datetime, timedelta

# === CONFIG ===
start_time = datetime(2025, 4, 25, 0, 0)   # Set your start time (UTC)
end_time = datetime(2025, 4, 28, 6, 0)     # Set your end time (UTC)
output_dir = "./mrms_qpe"                  # Local directory to save files
base_url = "https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00"

# Make sure output directory exists
os.makedirs(output_dir, exist_ok=True)

# MRMS files are usually named like: MultiSensor_QPE_01H_Pass2_00.00_YYYYMMDD-HHMM.grib2.gz
current_time = start_time
while current_time <= end_time:
    day_str = current_time.strftime("%Y%m%d")
    filename = f"MRMS_MultiSensor_QPE_01H_Pass2_00.00_{current_time.strftime('%Y%m%d-%H%M%S')}.grib2.gz"
    file_url = f"{base_url}/{day_str}/{filename}"
    local_path = os.path.join(output_dir, filename)
    
    print(f"Downloading {filename}...")
    response = requests.get(file_url, stream=True)
    
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved to {local_path}")
    else:
        print(f"Failed to download {filename} (HTTP {response.status_code})")
    
    current_time += timedelta(hours=1)

# ex link: https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/20250425/MRMS_MultiSensor_QPE_01H_Pass2_00.00_20250425-000000.grib2.gz
# bad link https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/20250425/MRMS_MultiSensor_QPE_01H_Pass2_00.00_20250425-000000.grib2.gz'
