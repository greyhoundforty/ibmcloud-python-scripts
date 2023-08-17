import SoftLayer
from rich.table import Table
from rich.console import Console

client = SoftLayer.create_client_from_env()

vgs = client['Account'].getVirtualGuests()
filtered_vgs = [s for s in vgs if s.get('primaryIpAddress')]
# Create tables 
vstable = Table(title="Virtual Servers")

# Add columns for our table
vstable.add_column("ID")
vstable.add_column("Hostname")
vstable.add_column("Public IP")
vstable.add_column("OS")
vstable.add_column("Provision Date")


# Loop through vgs
for vg in filtered_vgs:
  vg_id = vg['id']
  object_mask = "mask[id,operatingSystem[softwareLicense[softwareDescription]]]"
  vg_details = client['Virtual_Guest'].getObject(
  	id=vg_id,
	 mask=object_mask
	)
  hostname = vg['hostname']
  os_data = vg_details.get('operatingSystem')
  os_ref_code = "NOT FOUND" if os_data is None else os_data['softwareLicense']['softwareDescription']['referenceCode']
  prov_date = vg['provisionDate']
  ip = vg.get('primaryIpAddress')
  # Add row  
  vstable.add_row(str(vg_id), str(hostname), str(ip), str(os_ref_code), str(prov_date))


console = Console() 
console.print(vstable)
