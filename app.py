import SoftLayer
import socket
import threading

# Create client object
client = SoftLayer.Client()

def get_public_vms():
  vms = []
  virtual_guests = client['Account'].getVirtualGuests()
  
  for vg in virtual_guests:
    ip = vg.get('primaryIpAddress')
    if ip:
      vms.append(vg)

  return vms

def get_bare_metals():
    bms = []
    bare_metals = client['Account'].getHardware()
  
    for bm in bare_metals:
        ip = bm.get('primaryIpAddress')
        if ip:
            bms.append(bm)

    return bms
  

def check_port(ip, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((ip, port))
  sock.close()  
  return result


# def check_ports(ip):
#    threading.Thread(target=check_port, args=(ip, 22)).start()
#    threading.Thread(target=check_port, args=(ip, 3389)).start()

def scan_virtual_guests():
    print("Scanning virtual guests")
    public_vms = get_public_vms()
    for vm in public_vms:
  
        ip = vm['primaryIpAddress']

        port_22 = check_port(ip, 22)
        port_3389 = check_port(ip, 3389)

        if port_22 == 0:
            print(f"{ip} has open port 22")

        if port_3389 == 0:  
            print(f"{ip} has open port 3389")

def scan_bare_metals():
    print("Scanning bare metal servers")
    bare_metals = get_bare_metals()
    for bm in bare_metals:
  
        ip = bm['primaryIpAddress']

        port_22 = check_port(ip, 22)
        port_3389 = check_port(ip, 3389)

        if port_22 == 0:
            print(f"{ip} has open port 22")

        if port_3389 == 0:  
            print(f"{ip} has open port 3389")

try:
    scan_virtual_guests()
    scan_bare_metals()
except SoftLayer.SoftLayerAPIError as e:
    print("Unable to get account information. "
          % (e.faultCode, e.faultString))
    exit(1)
