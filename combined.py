import SoftLayer
from rich.table import Table
from rich.console import Console
import socket
import threading

client = SoftLayer.create_client_from_env()

vgs = client['Account'].getVirtualGuests()
bms = client['Account'].getHardware()

def check_port(ip, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((ip, port))
  return result == 0

# Create tables 
vstable = Table(title="Virtual Servers")
bmtable = Table(title="Bare Metal Servers") 

# Add columns to both
vstable.add_column("ID")
vstable.add_column("Hostname")
vstable.add_column("OS")
vstable.add_column("Provision Date")
vstable.add_column("IP")
vstable.add_column("Open SSH/RDP Port")
bmtable.add_column("ID")

# Loop through vgs
for vg in vgs:
  vg_id = vg['id']
  vg_ip = vg.get('primaryIpAddress')
  if not vg_ip:
    continue
  port_22_open = check_port(vg_ip, 22) 
  port_3389_open = check_port(vg_ip, 3389)

  if port_22_open or port_3389_open:
    port_status = "Y"
  else:
    port_status = "N"
  object_mask = "mask[id,operatingSystem[softwareLicense[softwareDescription]]]"
  vg_details = client['Virtual_Guest'].getObject(
	 id=vg_id,
	 mask=object_mask
	)
  hostname = vg['hostname']
  os_data = vg_details.get('operatingSystem')
  os_ref_code = "NOT FOUND" if os_data is None else os_data['softwareLicense']['softwareDescription']['referenceCode']
  prov_date = vg['provisionDate']

  # Add row  
  vstable.add_row(str(vg_id), str(hostname), str(os_ref_code), str(prov_date), str(vg_ip), str(port_status))



# for vg in vgs:
#   vg_id = vg['id']
#   object_mask = "mask[id,operatingSystem[softwareLicense[softwareDescription]]]"
#   vg_details = client['Virtual_Guest'].getObject(
# 	  id=vg_id,
# 	  mask=object_mask
# 	)
#   fqdn = vg['fullyQualifiedDomainName']
#   os_data = vg_details.get('operatingSystem')
#   os_ref_code = "NOT FOUND" if os_data is None else os_data['softwareLicense']['softwareDescription']['referenceCode']
#   prov_date = vg['provisionDate']
#   vstable = Table(title="Virtual Servers")
#   
#   vstable.add_column("ID")
#   vstable.add_column("FQDN")
#   vstable.add_column("OS")
#   vstable.add_column("Provision Date")
# 
#   vstable.add_row(
# 	str(vg_id), 
# 	str(fqdn),
# 	str(os_ref_code),
# 	str(prov_date)  
#   )
# 
# for bm in bms:
#   bm_id = bm['id']
#   object_mask = "mask[id,operatingSystem[softwareLicense[softwareDescription]]]"
#   bm_details = client['Hardware'].getObject(
# 	  id=bm_id,
# 	  mask=object_mask
# 	)
#   fqdn = bm['fullyQualifiedDomainName']
#   os_data = bm_details.get('operatingSystem')
#   os_ref_code = "NOT FOUND" if os_data is None else os_data['softwareLicense']['softwareDescription']['referenceCode']
#   prov_date = bm['provisionDate']
#   
#   bmtable.add_row(str(bm_id), str(fqdn), str(os_ref_code), str(prov_date))
# 
# #   bmtable = Table(title="Bare Metal Servers")
# #   bmtable.add_column("ID")
# #   bmtable.add_column("Hostname")
# #   bmtable.add_column("OS")
# #   bmtable.add_column("Provision Date")
# #	bmtable.add_column("Port 22 Open")
# #   bmtable.add_row(
# # 	str(bm_id), 
# # 	str(fqdn),
# # 	str(os_ref_code),
# # 	str(prov_date)  
# #   )
# # 
console = Console() 
console.print(vstable)