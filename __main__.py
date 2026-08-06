import pulumi 
import pulumi_proxmoxve as proxmoxve

config = pulumi.Config("proxmoxve")
endpoint = config.require("endpoint")
api_token = config.require_secret("apiToken")
vm_password = config.require_secret("password")


proxmox = proxmoxve.Provider(
    "proxmox",
    endpoint=endpoint,
    api_token=api_token)



triangle_nodes = [
    {"name": "triangle-1", "vmid": 121, "ip": "10.23.50.59/23"},
    {"name": "triangle-2", "vmid": 122, "ip": "10.23.50.60/23"},
    {"name": "triangle-3", "vmid": 123, "ip": "10.23.50.61/23"},
]

vms = []


for node in triangle_nodes:
    vm = proxmoxve.VmLegacy(f"proxmox-vm-{node['name']}",
        node_name="a1-crni",
        pool_id="intern",
        vm_id=node["vmid"],
        name=node["name"],
        description=f"{node['name']} of the triangle created with Pulumi",
        agent={"enabled": False},  # if false rhen less time creating the VM, but no guest agent features available
        clone={
                   "vm_id":"111",
               },
       disks=[{"interface": "scsi0", "size": 40,"datastore_id": "dps-a-vol-01"}],        
       cdrom={"file_id": "none", "interface": "ide2"},
        initialization={
            "type": "nocloud",
            "datastore_id": "dps-a-vol-01",
            "ip_configs": [{
                "ipv4": {
                    "address": node["ip"],
                    "gateway": "10.23.50.1",
                },
            }],
            "user_account": {
                "username": "root",
                "password": vm_password, 
            },
           
        },
        stop_on_destroy=True, 
        opts=pulumi.ResourceOptions(depends_on=vms[-1:]),
    )
    vms.append(vm)


pulumi.export("triangle_ips", [n["ip"] for n in triangle_nodes])