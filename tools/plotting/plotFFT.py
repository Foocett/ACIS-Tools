import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_dft_by_src(csv_path, src_filter=None, sensor="nox"):
    """
    Reads a CSV file and plots the DFT (magnitude) of either NOx Raw or O2 Raw vs. frequency for each unique Src as a separate line.
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
        ylabel = 'DFT Magnitude (NOx Raw)'
        title = 'DFT of NOx Raw by Src'
    elif sensor.lower() == "o2":
        value_col = 'O2 Raw' if 'O2 Raw' in df.columns else df.columns[8]
        ylabel = 'DFT Magnitude (O2 Raw)'
        title = 'DFT of O2 Raw by Src'
    else:
        raise ValueError("sensor argument must be either 'nox' or 'o2'")

    unique_srcs = df[src_col].unique() if src_filter is None else [
        src for src in df[src_col].unique() if src in src_filter]
    plt.figure(figsize=(12, 6))
    for src in unique_srcs:
        subset = df[df[src_col] == src]
        t = subset[time_col].values
        if len(t) < 2:
            continue
        dt = np.mean(np.diff(t))
        vals = subset[value_col].values
        if sensor.lower() == "nox":
            vals = 0.05 * vals - 200
        elif sensor.lower() == "o2":
            vals = 0.00054 * vals - 12
        fft_vals = np.fft.fft(vals)
        freqs = np.fft.fftfreq(len(vals), d=dt)
        plt.plot(freqs[:len(freqs)//2], np.abs(fft_vals)
                 [:len(fft_vals)//2], label=f'Src {src}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example usage
    csv_path = 'unattended_field_test.csv'
    plot_dft_by_src(csv_path, src_filter=[81, 82], sensor="nox")
    # Plot DFT for O2 Raw
    plot_dft_by_src(csv_path, src_filter=[81, 82], sensor="o2")
