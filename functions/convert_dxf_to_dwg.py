import subprocess
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for PyInstaller and dev """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def convert_dxf_to_dwg(input_file, output_folder):
    oda_converter = resource_path(os.path.join("ODA", "ODAFileConverter.exe"))

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_folder = os.path.dirname(input_file)
    file_filter = os.path.basename(input_file)

    command = [
        oda_converter,
        input_folder,
        output_folder,
        "ACAD2018",  # Output version
        "DWG",       # Format
        "0",         # No recursion
        "1",         # Audit
        file_filter  # Filter (filename)
    ]

    subprocess.run(command, check=True)
    print(f"✅ DXF converted to DWG and saved in: {output_folder}")