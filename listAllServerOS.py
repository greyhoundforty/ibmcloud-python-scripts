import SoftLayer
from operator import itemgetter

client = SoftLayer.create_client_from_env()

vgs = client['Account'].getVirtualGuests()
bms = client['Account'].getHardware()

object_mask = "mask[id,operatingSystem[softwareLicense[softwareDescription]]]"

for vg in vgs:
  vg_id = vg['id']
  vg_details = client['Virtual_Guest'].getObject(
    id=vg_id,
    mask=object_mask
  )
  
  os_data = vg_details.get('operatingSystem')
  
  if not os_data:
    print(f"{vg_id} - OS NOT FOUND")
    continue 
  
  os_name = os_data['softwareLicense']['softwareDescription']['name']
  print(vg_id, os_name)

for bm in bms:
  bm_id = bm['id']
  bm_details = client['Hardware'].getObject(
    id=bm_id,
    mask=object_mask
  )
  
  os_data = bm_details.get('operatingSystem')
  
  if not os_data:
    print(f"{bm_id} - OS NOT FOUND")
    continue 
  
  os_name = os_data['softwareLicense']['softwareDescription']['name']
  print(bm_id, os_name)
  

# for vg in vgs:
#   vg_id = vg['id']
#   vg_details = client['Virtual_Guest'].getObject(id=vg_id)
#   
#   print(vg_details['operatingSystem']['softwareLicense']['softwareDescription']['name'])
