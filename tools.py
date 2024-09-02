import psutil
import platform
import speedtest

def get_readable_file_size(size):
    return f"{size / (1024 ** 2):.2f} MB"

def get_speedtest_stats():
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        test.download()
        test.upload()
        test.results.share()
        result = test.results.dict()
        path = result['share']

        stats = f'''
➲ <b><i>SPEEDTEST INFO</i></b>
┠ <b>Upload:</b> <code>{get_readable_file_size(result['upload'] / 8)}/s</code>
┠ <b>Download:</b> <code>{get_readable_file_size(result['download'] / 8)}/s</code>
┠ <b>Ping:</b> <code>{result['ping']} ms</code>
┠ <b>Time:</b> <code>{result['timestamp']}</code>
┠ <b>Data Sent:</b> <code>{get_readable_file_size(int(result['bytes_sent']))}</code>
┖ <b>Data Received:</b> <code>{get_readable_file_size(int(result['bytes_received']))}</code>

➲ <b><i>SPEEDTEST SERVER</i></b>
┠ <b>Name:</b> <code>{result['server']['name']}</code>
┠ <b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
┠ <b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
┠ <b>Latency:</b> <code>{result['server']['latency']}</code>
┠ <b>Latitude:</b> <code>{result['server']['lat']}</code>
┖ <b>Longitude:</b> <code>{result['server']['lon']}</code>

➲ <b><i>CLIENT DETAILS</i></b>
┠ <b>IP Address:</b> <code>{result['client']['ip']}</code>
┠ <b>Latitude:</b> <code>{result['client']['lat']}</code>
┠ <b>Longitude:</b> <code>{result['client']['lon']}</code>
┠ <b>Country:</b> <code>{result['client']['country']}</code>
┠ <b>ISP:</b> <code>{result['client']['isp']}</code>
┖ <b>ISP Rating:</b> <code>{result['client']['isprating']}</code>
    '''
        return path, stats
    
    except speedtest.SpeedtestException as e:
        return None, f"Speedtest failed: {str(e)}"
    except KeyError as e:
        return None, f"KeyError: {str(e)} occurred while accessing results."
    except Exception as e:
        return None, f"An error occurred: {str(e)}"



def get_system_info():
    uname_info = platform.uname()
    cpu_info = {
        'Physical cores': psutil.cpu_count(logical=False),
        'Total cores': psutil.cpu_count(logical=True),
        'Max Frequency': f"{psutil.cpu_freq().max} MHz",
        'Min Frequency': f"{psutil.cpu_freq().min} MHz",
        'Current Frequency': f"{psutil.cpu_freq().current} MHz",
        'CPU Usage': f"{psutil.cpu_percent(interval=1)}%"
    }
    memory_info = {
        'Total Memory': f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        'Available Memory': f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
        'Used Memory': f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB",
        'Memory Usage': f"{psutil.virtual_memory().percent}%"
    }
    disk_info = {
        'Total Disk Space': f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB",
        'Used Disk Space': f"{psutil.disk_usage('/').used / (1024 ** 3):.2f} GB",
        'Free Disk Space': f"{psutil.disk_usage('/').free / (1024 ** 3):.2f} GB",
        'Disk Usage': f"{psutil.disk_usage('/').percent}%"
    }

    info_text = (
        f"System Information:\n"
        f"  System: {uname_info.system}\n"
        f"  Node Name: {uname_info.node}\n"
        f"  Release: {uname_info.release}\n"
        f"  Version: {uname_info.version}\n"
        f"  Machine: {uname_info.machine}\n"
        f"  Processor: {uname_info.processor}\n\n"
        
        f"CPU Information:\n"
        f"  Physical Cores: {cpu_info['Physical cores']}\n"
        f"  Total Cores: {cpu_info['Total cores']}\n"
        f"  Max Frequency: {cpu_info['Max Frequency']}\n"
        f"  Min Frequency: {cpu_info['Min Frequency']}\n"
        f"  Current Frequency: {cpu_info['Current Frequency']}\n"
        f"  CPU Usage: {cpu_info['CPU Usage']}\n\n"
        
        f"Memory Information:\n"
        f"  Total Memory: {memory_info['Total Memory']}\n"
        f"  Available Memory: {memory_info['Available Memory']}\n"
        f"  Used Memory: {memory_info['Used Memory']}\n"
        f"  Memory Usage: {memory_info['Memory Usage']}\n\n"
        
        f"Disk Information:\n"
        f"  Total Disk Space: {disk_info['Total Disk Space']}\n"
        f"  Used Disk Space: {disk_info['Used Disk Space']}\n"
        f"  Free Disk Space: {disk_info['Free Disk Space']}\n"
        f"  Disk Usage: {disk_info['Disk Usage']}"
    )

    return info_text

if __name__ == "__main__":
    print(get_system_info())
