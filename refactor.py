import SoftLayer
from rich.table import Table
from rich.console import Console
import socket
import csv
import time
from multiprocessing.pool import ThreadPool

# Filter servers 

def get_servers():
  try:
    print("Scanning account for virtual and bare metal servers")
    client = SoftLayer.create_client_from_env()
    vgs = client['Account'].getVirtualGuests() 
    bms = client['Account'].getHardware()
    servers = vgs + bms
    print(f"Total servers on account: {len(servers)} (virtual {len(vgs)}, bare metal {len(bms)})")
  
    return servers
  except SoftLayer.SoftLayerAPIError as e:
    print(f"Unable to get servers: {e}")
    return []

def filter_by_ip(servers):
  print("Filtering to servers with Public IPs")
  filtered = [s for s in servers if s.get('primaryIpAddress')]
  print(f"Found {len(filtered)} servers with public IPs")
  return filtered

def check_port(ip, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((ip, port))
  return result == 0


servers = get_servers()
filtered = filter_by_ip(servers)

ips = [server['primaryIpAddress'] for server in filtered]

def scan_ports(server):
  ip = server['primaryIpAddress']
  
  open_ports = []

  if check_port(ip, 22):
    open_ports.append(22)

  if check_port(ip, 80):  
    open_ports.append(80)

  if check_port(ip, 443):  
    open_ports.append(443)

  if check_port(ip, 3389):  
    open_ports.append(3389)


  if open_ports:
    print(f"{ip} has open ports: {open_ports}")

  return open_ports

pool = ThreadPool(10)
pool.map(scan_ports, filtered)

# Build table
table = Table()

table.add_column("Server ID")
table.add_column("Hostname")
table.add_column("Public IP")
table.add_column("Open Port")
table.add_column("Provision Date")

for server in filtered:

  open_ports = scan_ports(server)

  if open_ports:

    table.add_row(
      str(server['id']),
      server['hostname'],
      server['primaryIpAddress'],
      str(open_ports[0]),
      server['provisionDate']  
    )

# Print table 
console = Console()
console.print(table)

with open('servers.csv', 'w', newline='') as f:
  writer = csv.writer(f)
  
  # Write header
  writer.writerow(table.columns)
  
  # Write rows  
  for row in table.rows:
    writer.writerow(row)