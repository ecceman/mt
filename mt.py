#!/usr/bin/env python

__author__ = "ecceman"
__license__ = "MIT License"
__status__ = "Testing"

from netmiko import ConnectHandler, NetmikoTimeoutException
from getpass import getpass
import argparse
import validators
import re


def strip_chars(input_str: str) -> str:
    s = input_str.replace('[', '')
    s = s.replace(']', '')
    s = s.replace("'", '')
    s = s.replace('#', '')
    s = s.replace('>', '')
    return s


def find_mac(mac_address: str, device_ip: str, device_type="cisco_ios") -> bool:
    cisco_mac = re.sub('[^a-f\d]', '', mac_address)
    cisco_mac = cisco_mac[:4] + '.' + cisco_mac[4:8] + '.' + cisco_mac[8:]
    print('Looking for : ' + cisco_mac + ' on ' + device_ip)

    try:
        device = {'device_type': device_type, 'host': device_ip, 'username': args.user, 'password': password}
        with ConnectHandler(**device) as c:
            mac_result = c.send_command('show mac address-table | i ' + cisco_mac)
            if len(mac_result) > 1 and '^' not in mac_result:
                rows = mac_result.strip().split('\n')
                mac_iface = rows[0].split()[-1]
                # Is there a neighboring switch on this interface?
                cdp_neighbor = c.send_command('show cdp ne ' + mac_iface + ' detail').strip().split('\n')
                if len(cdp_neighbor) > 1 and '^' not in cdp_neighbor:
                    neighbor = {}
                    for row in cdp_neighbor:
                        row = row.strip()
                        if row.startswith('Device ID'):
                            neighbor['device_id'] = row.split()[2]
                        if row.startswith('IP address:'):
                            neighbor['ip_address'] = row.split()[2]
                        if row.startswith('Platform'):
                            neighbor['platform'] = row
                            break
                    print('Found a trail: ' + strip_chars(c.find_prompt()) + " " + mac_iface + " leading to " + neighbor['device_id'] + " ("+ neighbor['platform'] + ") on " + neighbor['ip_address'])
                    follow = input("Follow? (y/n) ")
                    if follow == "y":
                        find_mac(cisco_mac, neighbor['ip_address'])
                else:
                    print('Found it! ' + strip_chars(c.find_prompt()) + ', port ' + mac_iface)
                    # Do we have an IP for this MAC address?
                    if args.router:
                        device_ips = find_ip(cisco_mac)
                        if len(device_ips) > 0:
                            for ip in device_ips:
                                print('Device IPs found: ' + ip['ip'] + ' ' + ip['vlan'])
                return True
            else:
                print('MAC address not found on device ' + device_ip)
                return False
    except NetmikoTimeoutException as e:
        if device_type == 'cisco_ios':
            find_mac(mac_address, device_ip, device_type='cisco_ios_telnet')
        else:
            print("Connection to " + device_ip + "failed: " + e)
            return False
    except Exception as e:
        print('General Exception: ' + str(e))
        return False


def find_ip(mac_address: str) -> list:
    device_ips = []
    try:
        print('Trying to find IP for ' + mac_address + "... ")
        router = {'device_type': 'cisco_ios', 'host': args.router, 'username': args.user, 'password': password}
        with ConnectHandler(**router) as r:
            arp_table = r.send_command('show ip arp | i ' + mac_address)
            if len(arp_table) > 1 and '^' not in arp_table:
                arp_rows = arp_table.split('\n')
                device_ips = []
                for arp_entry in arp_rows:
                    arp_entry_split = arp_entry.split()
                    device_ips.append({'ip': arp_entry_split[1], 'vlan': arp_entry_split[5]})
    except Exception as e:
        print('General Exception: ' + str(e))
    finally:
        return device_ips


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAC address tracker')
    parser.add_argument('mac_address', help='MAC address  to find')
    parser.add_argument('switch_ip', help='Specific switch IP or list of IP addresses')
    parser.add_argument('--user', type=str, help='username')
    parser.add_argument('--router', type=str, help='Router IP')
    args = parser.parse_args()

    if validators.mac_address(args.mac_address) or re.match('^[a-f0-9]{4}.[a-f0-9]{4}.[a-f0-9]{4}$', args.mac_address, re.IGNORECASE):
        if validators.ipv4(args.switch_ip):
            password = getpass(prompt='Password for ' + args.switch_ip + ': ', stream=None)
            find_mac(args.mac_address, args.switch_ip)
