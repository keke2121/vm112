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
    {"name": "triangle-1", "vmid": 121, "ip": "10.23.50.59/23", "mac": "BC:24:11:00:CF:96"},
    {"name": "triangle-2", "vmid": 122, "ip": "10.23.50.60/23", "mac": "BC:24:11:00:CF:97"},
    {"name": "triangle-3", "vmid": 123, "ip": "10.23.50.61/23", "mac": "BC:24:11:00:CF:98"},
]

vms = []

for node in triangle_nodes:
    vm = proxmoxve.VmLegacy(f"proxmox-vm-{node['name']}",
        node_name="a1-crni",
        pool_id="intern",
        vm_id=node["vmid"],
        name=node["name"],
        description=f"{node['name']} of the triangle created with Pulumi",
        agent={"enabled": False}, 
        clone={
            "vm_id": "114", 
        },
        disks=[{
            "interface": "scsi0", 
            "size": 40,
            "datastore_id": "dps-a-vol-01"
        }],
        network_devices=[{
            "bridge": "vlan407",
            "mac_address": node["mac"],
            "model": "virtio",
            "mtu": 1
        }],
        stop_on_destroy=True, 
        opts=pulumi.ResourceOptions(depends_on=vms[-1:]),
    )
    vms.append(vm)