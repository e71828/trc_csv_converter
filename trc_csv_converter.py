#!/usr/bin/env python3  
# -*- coding: utf-8 -*- 
#----------------------------------------------------------------------------
# Created By  : Xiao Zhu  
# Created Date: 1/5/2023
# Modified by: ChatGPT  
# Version: '0.0.3'
# ---------------------------------------------------------------------------

import csv
import timeit
import os
import glob

# Get the directory containing the .trc files
trc_directory = input("Enter the directory path containing .trc files: ")

# Get all .trc files in the directory
trc_files = glob.glob(os.path.join(trc_directory, '*.trc'))

# Construct the header for the new CAN trace in .CSV file
header_list = ['Message Number', 'Time Offset(ms)', 'Bus', 'Type', 'ID (hex)', 'Data Length',
               'Byte0', 'Byte1', 'Byte2', 'Byte3', 'Byte4', 'Byte5', 'Byte6', 'Byte7']

start = timeit.default_timer()

# Function to convert a byte from hex to decimal
def hex_to_decimal(hex_string):
    try:
        # Convert hex to decimal if not empty
        return str(int(hex_string, 16)) if hex_string else ''
    except ValueError:
        return ''  # Handle any invalid hex string cases

# Loop through each .trc file and convert it to .csv
for trc_file in trc_files:
    csv_filename = os.path.splitext(trc_file)[0] + '.csv'  # Create the CSV filename based on the .trc filename

    with open(trc_file, 'r') as f1, open(csv_filename, 'w', newline="") as f2:
        print(f'Converting {trc_file} to {csv_filename}...')
        lines = f1.readlines()

        # Write the header to the CSV file
        writer = csv.DictWriter(f2, fieldnames=header_list)
        writer.writeheader()

        for line in lines:
            # Filter out TRC file headers
            if list(line)[0] != ';':
                line_split = line.split()

                # Pad with empty strings if CAN message is less than 8 bytes
                while len(line_split) < 15:
                    line_split.append('')

                # Convert the bytes from hexadecimal to decimal
                bytes_in_decimal = [hex_to_decimal(byte) for byte in line_split[7:15]]

                # Write each row to the CSV file
                writer.writerow({
                    'Message Number': line_split[0],
                    'Time Offset(ms)': line_split[1],
                    'Bus': line_split[2],
                    'Type': line_split[3],
                    'ID (hex)': line_split[4],
                    'Data Length': line_split[6],
                    'Byte0': bytes_in_decimal[0], 'Byte1': bytes_in_decimal[1],
                    'Byte2': bytes_in_decimal[2], 'Byte3': bytes_in_decimal[3],
                    'Byte4': bytes_in_decimal[4], 'Byte5': bytes_in_decimal[5],
                    'Byte6': bytes_in_decimal[6], 'Byte7': bytes_in_decimal[7]
                })

stop = timeit.default_timer()
print('All files converted successfully.')
print('Total Processing Time (Seconds): ', stop - start)
