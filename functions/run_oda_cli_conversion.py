import subprocess
import os

# Path to ODAFileConverter.exe
ODA_PATH = r"C:\Program Files\ODA\ODAFileConverter 25.12.0\ODAFileConverter.exe"

# Input and output folders
INPUT_FOLDER = r"C:\Users\g.dempsey\Desktop\DWG_Input"
OUTPUT_FOLDER = r"C:\Users\g.dempsey\Desktop\DWG_Output"

# ODA Converter parameters
DXF_VERSION = "ACAD2018"
OUTPUT_FORMAT = "DXF"
RECURSE = "0"
AUDIT = "1"
FILTER = "*.DWG"

# Full CLI command
command = [
    ODA_PATH,
    INPUT_FOLDER,
    OUTPUT_FOLDER,
    DXF_VERSION,
    OUTPUT_FORMAT,
    RECURSE,
    AUDIT,
    FILTER
]

print("🔄 Running ODA File Converter...")
result = subprocess.run(command, shell=True)

if result.returncode == 0:
    print("✅ Conversion complete.")
else:
    print("❌ Something went wrong.")