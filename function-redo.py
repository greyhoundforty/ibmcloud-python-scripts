import SoftLayer
from rich.table import Table
from rich.console import Console
import socket
import csv
import time
# Reusable functions
from multiprocessing.pool import ThreadPool

# Filter servers 

def get_servers():
  try:
    print("Getting servers")
    client = SoftLayer.create_client_from_env()
    vgs = client['Account'].getVirtualGuests() 
    bms = client['Account'].getHardware()
    servers = vgs + bms
    print(f"Total servers scanned: {len(servers)}")
  
    return servers
  except SoftLayer.SoftLayerAPIError as e:
    print(f"Unable to get servers: {e}")
    return []

def filter_by_ip(servers):
  print("Filtering to servers with Public IPs..")
  filtered = [s for s in servers if s.get('primaryIpAddress')]
  print(f"Found {len(filtered)} servers with public IPs")
  return filtered

def get_os_port(server):
  try: 
    os_ref = server['operatingSystem']['softwareLicense']['softwareDescription']['referenceCode']
    if os_ref.startswith("WIN_"):
      print(f"Found Windows server: {server['id']}, setting port to 3389")
      return 3389
    else:
      print(f"Found Linux server: {server['id']}, setting port to 22")
      return 22 
  except KeyError:
    return None

def check_port(ip, port):
  print(f"Checking port {port} on {ip}")
  start = time.time()
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((ip, port))
  end = time.time()
  print(f"Port check took {end - start} seconds")
  return result == 0

def build_row(server):
  row = []

  server_id = server['id']
  row.append(str(server_id))

  hostname = server['hostname']
  row.append(hostname) 

  os_ref_code = "UNKNOWN"
  if 'operatingSystem' in server:
    os_data = server['operatingSystem']
    os_ref_code = os_data['softwareLicense']['softwareDescription']['referenceCode']
  row.append(os_ref_code)

  prov_date = server['provisionDate']
  row.append(str(prov_date))

  port = get_os_port(server) 
  row.append(str(port))

  return row

def print_table(table):
  console = Console() 
  console.print(table)
  # print table

def write_csv(table):
  with open('scanned_servers.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(table.columns)
    for row in table.rows:
        writer.writerow(row) # write csv
# Main logic


servers = get_servers()
filtered = filter_by_ip(servers)

open_ports = []

print("Scanning servers for open ports..")
for server in filtered:
  []
  ip = server['primaryIpAddress']
  
  port_22_open = check_port(ip, 22)
  if port_22_open:
    open_ports.append({'id': server['id'], 'port': 22})

  port_3389_open = check_port(ip, 3389)  
  if port_3389_open:
    open_ports.append({'id': server['id'], 'port': 3389})

table = Table()
table.add_column("ID")
table.add_column("Hostname")
table.add_column("Public IP")
table.add_column("Open Port") 
table.add_column("Provision Date")

for item in open_ports:
  server = [s for s in filtered if s['id'] == item['id']][0]
  
  table.add_row(
    str(item['id']),
    server['hostname'],
    server['primaryIpAddress'],
    str(item['port']), 
    str(server['provisionDate'])
  )

console = Console()
console.print(table)
