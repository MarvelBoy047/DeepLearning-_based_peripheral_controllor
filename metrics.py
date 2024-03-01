import tracemalloc
import psutil
import main_script as ms
import os
import matplotlib.pyplot as plt

def profile_main_script():
    # Get the process ID of the current script
    current_process = psutil.Process(os.getpid())

    # Start tracemalloc
    tracemalloc.start()

    # Run the main script (capturing the benchmarking metrics)
    ms.main()

    # Get memory usage after the script execution
    _, peak_memory = tracemalloc.get_traced_memory()

    # Get memory usage history
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    # Divide the data into segments
    num_segments = 3
    segment_size = len(top_stats) // num_segments

    # Plot memory usage over time for each segment
    for i in range(num_segments):
        start_index = i * segment_size
        end_index = (i + 1) * segment_size

        time_values = [stat.traceback[0].lineno for stat in top_stats[start_index:end_index]]
        size_values = [stat.size / (1024 * 1024) for stat in top_stats[start_index:end_index]]

        plt.plot(time_values, size_values)
        plt.xlabel('Line Number')
        plt.ylabel('Memory Usage (MB)')
        plt.title(f'Memory Usage Over Time (Segment {i + 1})')
        plt.show()

    # Print peak memory usage
    print("\nMemory Usage:")
    print(f"Peak Memory Usage: {peak_memory / (1024 * 1024):.2f} MB")

    # Include process-specific metrics
    process_memory_info = current_process.memory_info()

    print("\nProcess Metrics:")
    print(f"Process RAM Usage: {process_memory_info.rss / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    profile_main_script()
