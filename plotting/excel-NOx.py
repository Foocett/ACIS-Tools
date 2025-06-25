"""
excel-NOx.py

This script parses an Excel spreadsheet to extract and analyze NOx-related data from J1939 CAN logs.
It filters for rows where the PID (Parameter ID) in column G is 61454, extracts the first byte from the
space-separated hex data in column H, converts it to decimal, and plots the result against the time found in column B.

Requirements:
    - pandas
    - matplotlib

Usage:
    python excel-NOx.py

Output:
    - Prints a DataFrame with PID, raw data, first byte (hex), first byte (decimal), and first bit (if applicable)
    - Saves a plot as 'sample.png' in the current directory
"""

import pandas as pd
import matplotlib.pyplot as plt

# Path to your Excel file
EXCEL_PATH = r'_var_tmp_MGate5118_j1939_cap (1).xlsx'

# Read the Excel file (assumes first sheet)
df = pd.read_excel(EXCEL_PATH)

# Only use data starting from row 1 (change iloc if you want to skip rows)
df = df.iloc[0:]

# Define column indices (0-based): G = 6, H = 7, B = 1
col_pid = df.columns[6]   # Column G: PID
col_data = df.columns[7]  # Column H: Data
col_time = df.columns[1]  # Column B: Time

# Filter for PID == 61454
filtered = df[df[col_pid] == 61454]

def get_first_bit(byte_str):
    """
    Extracts the first bit from an 8-bit binary string.
    Returns None if not a valid 8-bit binary string.
    """
    if isinstance(byte_str, str) and len(byte_str) == 8 and set(byte_str) <= {'0', '1'}:
        return byte_str[0]
    return None

def get_first_byte(byte_str):
    """
    Extracts the first byte from a space-separated hex string (e.g., 'BD 0F D6 ...').
    Returns the first byte as a string, or None if not valid.
    """
    if isinstance(byte_str, str):
        parts = byte_str.strip().split()
        if len(parts) > 0 and all(len(b) == 2 for b in parts):
            return parts[0]
    return None

# Extract first bit (if data is 8-bit binary)
filtered = filtered.copy()
filtered['FirstBit'] = filtered[col_data].apply(get_first_bit)

# Extract first byte (space-separated hex)
filtered['FirstByte'] = filtered[col_data].apply(get_first_byte)

# Convert first byte to decimal
filtered['FirstByteDecimal'] = filtered['FirstByte'].apply(lambda x: int(x, 16) if isinstance(x, str) else None)

# Print results
print(filtered[[col_pid, col_data, 'FirstByte', 'FirstByteDecimal', 'FirstBit']])

# Plot FirstByteDecimal vs. Time
plot_data = filtered.dropna(subset=['FirstByteDecimal', col_time])
plt.figure(figsize=(10, 4))
plt.plot(plot_data[col_time], plot_data['FirstByteDecimal'], marker='o', linestyle='-', label='First Byte (Decimal)')
plt.xlabel('Time')
plt.ylabel('First Byte (Decimal)')
plt.title('First Byte (Decimal) vs. Time (PID 61454)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('sample.png')
plt.show()

# Optionally, save to CSV
# filtered[[col_pid, col_data, 'FirstByte', 'FirstByteDecimal', 'FirstBit']].to_csv('first_bytes_61454.csv', index=False)
