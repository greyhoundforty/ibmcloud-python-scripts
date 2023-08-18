import SoftLayer
from rich.table import Table
from rich.console import Console

client = SoftLayer.create_client_from_env()

bms = client['Account'].getHardware()

# Create tables 
bmtable = Table(title="All Bare Metal Servers")

# Add columns for our table
bmtable.add_column("ID")
bmtable.add_column("Hostname")
bmtable.add_column("Public IP")
bmtable.add_column("OS")
bmtable.add_column("Provision Date")


# Loop through BMs
for bm in bms:
  bm_id = bm['id']
  object_mask = "mask[id,operatingSystem[softwareLicense[softwareDescription]]]"
  bm_details = client['Hardware'].getObject(
  	id=bm_id,
	 mask=object_mask
	)
  hostname = bm['hostname']
  os_data = bm_details.get('operatingSystem')
  os_ref_code = "NOT FOUND" if os_data is None else os_data['softwareLicense']['softwareDescription']['referenceCode']
  prov_date = bm['provisionDate']
  ip = bm.get('primaryIpAddress')
  if ip:
    ip_str = str(ip)
  else:
    ip_str = "N/A"

  # Add row  
  bmtable.add_row(str(bm_id), str(hostname), str(ip_str), str(os_ref_code), str(prov_date))


console = Console() 
console.print(bmtable)
