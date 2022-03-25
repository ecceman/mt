# mt
MAC address tracker

```
$ python mt.py 01:05:02:5a:20:1b 10.19.254.1 --user admin

Password for 10.191.254.1:
Looking for : 01:05:02:5a:20:1b on 10.19.254.1
Found a trail: switch1 Te1/0/10 leading to switch3 (Platform: cisco WS-C3750G-12S,  Capabilities: Switch IGMP) on 10.19.254.4
Follow? (y/n) y

Looking for : 01:05:02:5a:20:1b on 10.19.254.4
Found a trail: switch3 Gi1/0/11 leading to switch11 (Platform: cisco WS-C2960X-24TS-L,  Capabilities: Switch IGMP) on 10.19.254.11
Follow? (y/n) y

Looking for : 01:05:02:5a:20:1b on 10.19.254.11
Found a trail: switch11 Gi1/0/26 leading to switch12 (Platform: cisco WS-C2960X-24TS-L,  Capabilities: Switch IGMP) on 10.19.254.12
Follow? (y/n) y

Looking for : 01:05:02:5a:20:1b on 10.19.254.12

Found it! switch12, port Gi1/0/2
```