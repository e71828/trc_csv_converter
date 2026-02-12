#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Created By  : Xiao Zhu  
# Created Date: 1/5/2023
# Modified by: ChatGPT  
# Version: '0.0.3'
# ---------------------------------------------------------------------------

import csv
import getopt
import sys
import timeit
import os
import glob


# Function to convert a byte from hex to decimal
def hex_to_decimal(hex_string):
    try:
        # Convert hex to decimal if not empty
        return int(hex_string, 16) if hex_string else 0
    except ValueError or TypeError:
        return 255


def trc2csv_slew_calib(trc_tree):
    # Get all .trc files in the directory
    trc_files = glob.glob(os.path.join(trc_tree, '*.trc'))

    header_list = ['actual_slew_velocity(X)',
                   'actual_slew_velocity(Y)',
                   'Desired_Y_slew(X)',
                   'Desired_Y_slew(Y)',
                   'tangjinfeng_wave_value(X)',
                   'tangjinfeng_wave_value(Y)',
                   'Y_slew(X)',
                   'Y_slew(Y)']
    start = timeit.default_timer()

    # Loop through each .trc file and convert it to .csv
    for trc_file in trc_files:
        csv_filename = os.path.splitext(trc_file)[0] + '.csv'  # Create the CSV filename based on the .trc filename

        with open(trc_file, 'r') as f1, open(csv_filename, 'w', newline="") as f2:
            print(f'Converting {trc_file} to {csv_filename}...')
            lines = f1.readlines()

            # Write the header to the CSV file
            writer = csv.DictWriter(f2, fieldnames=header_list)
            writer.writeheader()
            # 初始化在循环外
            cache_184 = False
            cache_calib = False
            for line in lines:
                line = line.strip()  # 去掉首尾不可见的空格、换行符
                if not line or line.startswith(';'): continue
                line_split = line.split()

                # if CAN message is less than 8 bytes
                if len(line_split) != 15: continue

                # Convert the bytes from hexadecimal to decimal
                bytes_in_decimal = [hex_to_decimal(byte) for byte in line_split[7:15]]
                can_id = line_split[4]
                timestamp_offset = line_split[1]
                if can_id == '0184':
                    cache_184 = True
                    # 假设该报文中包含 Y_slew 和 Desired_Y_slew，范围为 0~1000
                    timestamp_offset_184 = timestamp_offset
                    y_slew_left = int.from_bytes(bytes_in_decimal[0:2], byteorder='little', signed=False)
                    desired_y_slew_left = int.from_bytes(bytes_in_decimal[2:4], byteorder='little', signed=False)
                    y_slew_right = int.from_bytes(bytes_in_decimal[4:6], byteorder='little', signed=False)
                    desired_y_slew_right = int.from_bytes(bytes_in_decimal[6:8], byteorder='little', signed=False)
                    # 逻辑选择：优先取大
                    desired_y_slew = desired_y_slew_right if desired_y_slew_left < 20 else desired_y_slew_left
                    y_slew = y_slew_right if y_slew_left < 20 else y_slew_left
                elif can_id == '03C0':
                    cache_calib = True
                    timestamp_offset_calib = timestamp_offset
                    tangjinfeng_wave_value = int.from_bytes(bytes_in_decimal[4:6], byteorder='little', signed=True)
                    actual_slew_velocity = int.from_bytes(bytes_in_decimal[6:8], byteorder='little', signed=True) * 0.01

                if cache_calib and cache_184:
                    # Write each row to the CSV file
                    writer.writerow({
                        'actual_slew_velocity(X)': timestamp_offset_calib,
                        'actual_slew_velocity(Y)': f"{actual_slew_velocity:.2f}",
                        'Desired_Y_slew(X)': timestamp_offset_184,
                        'Desired_Y_slew(Y)': desired_y_slew,
                        'tangjinfeng_wave_value(X)': timestamp_offset_calib,
                        'tangjinfeng_wave_value(Y)': tangjinfeng_wave_value,
                        'Y_slew(X)': timestamp_offset_184,
                        'Y_slew(Y)': y_slew
                    })
                    # 写入后即刻重置，实现“丢弃重复 ID”并强制“交替处理”
                    cache_184 = cache_calib = False

            stop = timeit.default_timer()
            print('All files converted successfully.')
            print('Total Processing Time (Seconds): ', stop - start)


def trc2csv_decimal_decode(trc_tree):
    # Get all .trc files in the directory
    trc_files = glob.glob(os.path.join(trc_tree, '*.trc'))

    # Construct the header for the new CAN trace in .CSV file
    header_list = ['Message Number', 'Time Offset(ms)', 'Bus', 'Type', 'ID (hex)', 'Data Length',
                   'Byte0', 'Byte1', 'Byte2', 'Byte3', 'Byte4', 'Byte5', 'Byte6', 'Byte7']

    start = timeit.default_timer()

    # Loop through each .trc file and convert it to .csv
    for trc_file in trc_files:
        csv_filename = os.path.splitext(trc_file)[
                           0] + '.csv'  # Create the CSV filename based on the .trc filename

        with open(trc_file, 'r') as f1, open(csv_filename, 'w', newline="") as f2:
            print(f'Converting {trc_file} to {csv_filename}...')

            # Write the header to the CSV file
            writer = csv.DictWriter(f2, fieldnames=header_list)
            writer.writeheader()

            for line in f1:
                line = line.strip()  # 去掉首尾不可见的空格、换行符
                # Filter out TRC file headers
                if not line or line.startswith(';'): continue
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


if __name__ == '__main__':
    slew_calib = False
    trc_directory = ''
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "ct:", ["calib", "trc-folder="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in optlist:
        if opt in ['-c', '--calib']:
            slew_calib = True
        elif opt in ['-t', '--trc-folder']:
            trc_directory = arg.strip('"')
    if not trc_directory:
        print('No valid trc file path provided.')
        sys.exit(1)
    if slew_calib:
        trc2csv_slew_calib(trc_directory)
    else:
        trc2csv_decimal_decode(trc_directory)
