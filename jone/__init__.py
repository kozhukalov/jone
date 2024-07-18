import pyone
import click
import yaml
from pathlib import Path


@click.group()
def jone():
    pass


def session():
    p = Path.home() / ".config/jone/config"
    with p.open() as f:
        data = yaml.safe_load(f)
    endpoint = data["endpoint"]
    username = data["username"]
    password = data["password"]
    return pyone.OneServer(endpoint, session=f"{username}:{password}", https_verify=True)


def get_vms():
    one = session()
    vm_pool = one.vmpool.info(-2, -1, -1, -1)
    return sorted(vm_pool.VM, key=lambda x: x.NAME)


def get_vm_ips():
    return [vm.TEMPLATE["NIC"]["IP"] for vm in get_vms()]


@jone.command()
def pprint():
    for vm in get_vms():
        print(f"VM ID: {vm.ID}")
        print(f"VM Name: {vm.NAME}")
        print(f"VM State: {vm.STATE}")
        print(f"VM LCM State: {vm.LCM_STATE}")
        print(f"VM User: {vm.UNAME}")
        print(f"VM Group: {vm.GNAME}")
        # print(f"VM TEMPLATE: {vm.TEMPLATE}")
        nics = vm.TEMPLATE.get("NIC")
        if isinstance(nics, list):
            for nic in nics:
                print(f"VM IP Address: {nic["IP"]}")
        else:
            print(f"VM IP Address: {nics["IP"]}")
        print("-------------")


@jone.command()
def ansible_hosts():
    print("  hosts:")
    for vm in zip(("primary", "node-1", "node-2", "node-3"), get_vms()):
        print(f"    {vm[0]}:")
        print(f"      ansible_host: {vm[1].TEMPLATE["NIC"]["IP"]}")


@jone.command()
def all_ips():
    print(" ".join(get_vm_ips()))


@jone.command()
def cluster_ips():
    print(" ".join(get_vm_ips()[1:]))


@jone.command()
def primary_ip():
    print(get_vm_ips()[0])


@jone.command()
@click.argument('node', nargs=1, type=int)
def node_ip(node):
    print(get_vm_ips()[node])
