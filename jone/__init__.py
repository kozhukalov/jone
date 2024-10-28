import pyone
import click
import yaml
from pathlib import Path


@click.group()
@click.option("--label", "-l", multiple=True,
              help="Filter VMs by user labels")
@click.pass_context
def jone(ctx, label):
    ctx.ensure_object(dict)
    ctx.obj['labels'] = label


def session():
    p = Path.home() / ".config/jone/config"
    with p.open() as f:
        data = yaml.safe_load(f)
    endpoint = data["endpoint"]
    username = data["username"]
    password = data["password"]
    return pyone.OneServer(endpoint, session=f"{username}:{password}", https_verify=True)


def get_vms(labels=None):
    one = session()
    vm_pool = one.vmpool.info(-2, -1, -1, -1)
    vms = vm_pool.VM
    if labels:
        vms = []
        for vm in vm_pool.VM:
            vm_labels = vm.USER_TEMPLATE.get("LABELS", "").split()
            for l in labels:
                if l in vm_labels:
                    vms.append(vm)
    return sorted(vms, key=lambda x: x.NAME)


def get_vm_ips(labels=None):
    return [vm.TEMPLATE["NIC"]["IP"] for vm in get_vms(labels)]


@jone.command()
@click.pass_context
def pprint(ctx):
    for vm in get_vms(ctx.obj['labels']):
        print(f"VM ID: {vm.ID}")
        print(f"VM Name: {vm.NAME}")
        print(f"VM State: {vm.STATE}")
        print(f"VM LCM State: {vm.LCM_STATE}")
        print(f"VM User: {vm.UNAME}")
        print(f"VM Group: {vm.GNAME}")
        print(f"VM Labels: {vm.USER_TEMPLATE.get("LABELS")}")
        # print(f"VM TEMPLATE: {vm.TEMPLATE}")
        nics = vm.TEMPLATE.get("NIC")
        if isinstance(nics, list):
            for nic in nics:
                print(f"VM IP Address: {nic["IP"]}")
        else:
            print(f"VM IP Address: {nics["IP"]}")
        print("-------------")


@jone.command()
@click.pass_context
def ansible_hosts(ctx):
    print("  hosts:")
    for vm in zip(("primary", "node-1", "node-2", "node-3"), get_vms(ctx.obj['labels'])):
        print(f"    {vm[0]}:")
        print(f"      ansible_host: {vm[1].TEMPLATE["NIC"]["IP"]}")


@jone.command()
@click.pass_context
def all_ips(ctx):
    print(" ".join(get_vm_ips(ctx.obj['labels'])))


@jone.command()
@click.pass_context
def cluster_ips(ctx):
    print(" ".join(get_vm_ips(ctx.obj['labels'])[1:]))


@jone.command()
@click.pass_context
def primary_ip(ctx):
    print(get_vm_ips(ctx.obj['labels'])[0])


@jone.command()
@click.pass_context
@click.argument('node', nargs=1, type=int)
def node_ip(ctx, node):
    print(get_vm_ips(ctx.obj['labels'])[node])
