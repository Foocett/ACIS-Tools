import pandas as pd
import matplotlib.pyplot as plt
from AcisCanTools import utils
import binascii

def plot_by_src(csv_path, src_filter=None, sensor="nox"):
    """
    Reads a CSV file and plots either NOx or O2 raw value vs. time for each unique Src as a separate line.
    Optionally, only plots lines for Src values in src_filter.
    Args:
        csv_path (str): Path to the CSV file.
        src_filter (list, optional): List of Src values to plot. If None, plot all.
        sensor (str): 'nox' to plot NOx Raw, 'o2' to plot O2 Raw.
    """
    df = pd.read_csv(csv_path)
    time_col = 'Time' if 'Time' in df.columns else df.columns[2]
    src_col = 'Src' if 'Src' in df.columns else df.columns[4]
    if sensor.lower() == "nox":
        value_col = 'NOx Raw' if 'NOx Raw' in df.columns else df.columns[7]
        ylabel = 'NOx Raw Value'
        title = 'NOx Raw Value vs. Time by Src'
    elif sensor.lower() == "o2":
        value_col = 'O2 Raw' if 'O2 Raw' in df.columns else df.columns[8]
        ylabel = 'O2 Raw Value'
        title = 'O2 Raw Value vs. Time by Src'
    else:
        raise ValueError("sensor argument must be either 'nox' or 'o2'")

    unique_srcs = df[src_col].unique() if src_filter is None else [src for src in df[src_col].unique() if src in src_filter]
    plt.figure(figsize=(10, 6))
    for src in unique_srcs:
        subset = df[df[src_col] == src]
        yvals = subset[value_col]
        if sensor.lower() == "nox":
            yvals = 0.05 * yvals - 200
        elif sensor.lower() == "o2":
            yvals = 0.00054 * yvals - 12
        plt.plot(subset[time_col], yvals, label=f'Src {src}')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_by_pgn(csv_path, pgn_filter=None, sensor="nox"):
    """
    Reads a CSV file and plots either NOx or O2 raw value vs. time for each unique PGN as a separate line.
    Optionally, only plots lines for PGN values in pgn_filter.
    Args:
        csv_path (str): Path to the CSV file.
        pgn_filter (list, optional): List of PGN values to plot. If None, plot all.
        sensor (str): 'nox' to plot NOx Raw, 'o2' to plot O2 Raw.
    """
    df = pd.read_csv(csv_path)
    time_col = 'Time' if 'Time' in df.columns else df.columns[2]
    pgn_col = 'PGN' if 'PGN' in df.columns else df.columns[6]
    if sensor.lower() == "nox":
        value_col = 'NOx Raw' if 'NOx Raw' in df.columns else df.columns[7]
        ylabel = 'NOx Raw Value'
        title = 'NOx Raw Value vs. Time by PGN'
    elif sensor.lower() == "o2":
        value_col = 'O2 Raw' if 'O2 Raw' in df.columns else df.columns[8]
        ylabel = 'O2 Raw Value'
        title = 'O2 Raw Value vs. Time by PGN'
    else:
        raise ValueError("sensor argument must be either 'nox' or 'o2'")

    unique_pgns = df[pgn_col].unique() if pgn_filter is None else [pgn for pgn in df[pgn_col].unique() if pgn in pgn_filter]
    plt.figure(figsize=(10, 6))
    for pgn in unique_pgns:
        subset = df[df[pgn_col] == pgn]
        yvals = subset[value_col]
        if sensor.lower() == "nox":
            yvals = 0.05 * yvals - 200
        elif sensor.lower() == "o2":
            yvals = 0.00054 * yvals - 12
        plt.plot(subset[time_col], yvals, label=f'PGN {pgn}')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_by_src_raw(csv_path, src_filter=None, sensor="nox"):
    """
    Plots NOx or O2 from a CSV file where the data is in a raw hex format and must be decoded using AcisCanTools.utils.static_decode.
    Args:
        csv_path (str): Path to the CSV file.
        src_filter (list, optional): List of Src values to plot. If None, plot all.
        sensor (str): 'nox' or 'o2'.
    """
    df = pd.read_csv(csv_path)
    time_col = 'Time' if 'Time' in df.columns else df.columns[1]
    src_col = 'Src' if 'Src' in df.columns else df.columns[4]
    data_col = 'Data' if 'Data' in df.columns else df.columns[-1]
    ylabel = 'NOx Raw Value' if sensor.lower() == 'nox' else 'O2 Raw Value'
    title = f'{ylabel} vs. Time by Src (Decoded)'
    if src_filter is not None:
        df = df[df[src_col].isin(src_filter)]
    unique_srcs = df[src_col].unique()
    plt.figure(figsize=(10, 6))
    for src in unique_srcs:
        subset = df[df[src_col] == src]
        times = subset[time_col]
        decoded_vals = []
        for raw in subset[data_col]:
            try:
                # Remove spaces and decode hex string to bytes
                raw_bytes = binascii.unhexlify(str(raw).replace(' ', ''))
                decoded = utils.static_decode(raw_bytes)
                if sensor.lower() == 'nox':
                    val = 0.05 * decoded[0] - 200
                elif sensor.lower() == 'o2':
                    val = 0.00054 * decoded[1] - 12
                else:
                    val = None
                print(raw)
                print(raw_bytes)
                print(decoded)
                print(val)
                decoded_vals.append(val)
            except Exception:
                print("exception")
                decoded_vals.append(None)
        plt.plot(times, decoded_vals, label=f'Src {src}')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    # Example usage
    #plot_by_src('unattended_field_test.csv', [81, 82], sensor="nox")
    plot_by_src_raw('external_data.csv', src_filter=[17, 30], sensor="nox")
    #plot_by_src('field_test.csv', [81, 82], sensor="o2")
