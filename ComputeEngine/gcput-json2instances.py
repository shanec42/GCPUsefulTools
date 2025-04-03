#!/usr/bin/env python3
# vim: set ft=python tabstop=2 softtabstop=2 shiftwidth=2 expandtab :
#
# SPDX-FileCopyrightText: 2024 Shane Chambers <license@AustinLinux.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Input: json file containing compute engine instanes
# ie: gcloud compute instances describe <INSTANCE_NAME> --format=json
#
# Expected output: gcloud compute instances create <INSTANCE_NAME>
# ie: gcloud compute instances create test-instance
#
#

import argparse
import json
import re
import sys

shared_core_general_purpose_machine_types = [
  'e2-micro',
  'e2-small',
  'e2-medium',
  'f1-micro',
  'g1-small'
]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def diskOptions( disk):
  # [--disk=[auto-delete=AUTO-DELETE],
  #         [boot=BOOT],
  #         [device-name=DEVICE-NAME],
  #         [force-attach=FORCE-ATTACH],
  #         [mode=MODE],
  #         [name=NAME],
  #         [scope=SCOPE]
  # ]

  print(  "--disk='", end='')

  # [auto-delete=AUTO-DELETE]
  if ( f"{disk['autoDelete']}" == 'true'):
    print(  "auto-delete=yes", end=',')
  else:
    print(  "auto-delete=no", end=',')

  # [boot=BOOT]
  if ( f"{disk['boot']}" == 'true'):
    print(  "boot=yes", end=',')
  else:
    print(  "boot=no", end=',')

  # [device-name=DEVICE-NAME]
  # Default naming scheme is "persistent-disk-N"
  # If the deviceName is in this format, specific naming is not recommended
  persistent_disk_regex = re.compile( r'persistent-disk-\d+')
  if ( not persistent_disk_regex.match( disk['deviceName'])):
    print( f"device-name={disk['deviceName']}", end=',')

  # [force-attach=FORCE-ATTACH]
  if 'forceAttach' in disk:
    print(  "force-attach=yes", end=',')
  else:
    print(  "force-attach=no", end=',')

  # [mode=MODE]
  if ( f"{disk['mode']}" == 'READ_WRITE'):
    print(  "mode=rw", end=',')
  elif ( f"{disk['mode']}" == 'READ_ONLY'):
    print(  "mode=ro", end=',')

  # [name=NAME]
  # https://www.googleapis.com/compute/v1/projects/project-name/zones/us-east1-a/disks/disk-name-i-made-up
  disk_name_regex = re.compile( r'/compute/v1/projects/[^/]+/([^/]+)/[^/]+/[^/]+/([^$]+)')
  disk_name = disk_name_regex.search( disk['source']).group(2)
  print( f"name={disk_name}", end=',')

  # [scope=SCOPE]
  disk_scope = disk_name_regex.search( disk['source']).group(1)
  print( f"scope={disk_scope}", end=',')


def networkOptions( network):
  # [--network-interface=[PROPERTY=VALUE,...]]
  # [--network-interface=
  #         [address=EXTERNAL-ADDRESS | no-address],
  #         [network=NETWORK-NAME],
  #         [network-tier=[PREMIUM|STANDARD]],
  #         [private-netowrk-ip=RFC1918-ADDRESS],
  #         [subnet=SUBNET-OF-NETWORK-NAME],
  #         [nic-type=[GVNIC|VIRTIO_NET]],
  #         [queue-count=Rx-TX-QUEUE-SIZE],
  #         [stack-type=[IPV4_ONLY|IPV4_IPV6|IPV6_ONLY],
  #         [ipv6-network-tier=[PREMIUM]],
  #         [internal-ipv6-address=IPV6_ADDRESS],
  #         [internal-ipv6-prefix-length=INTERNAL_PREFIX_LENGTH],
  #         [external-ipv6-address=EXTERNAL_IPV6_ADDRESS],
  #         [internal-ipv6-prefix-length=EXTERNAL_PREFIX_LENGTH],
  #         [ipv6-public-ptr-domain=IPV6_CUSTOM_POINTER_DOMAIN],
  #         [alias=IP_ALIASES],
  #         [network-attachment=NETWORK_ATTACHMENT],
  # ]

  print(  "--network-interface='", end='')

  # [address=EXTERNAL-ADDRESS | no-address],


  # [network=NETWORK-NAME]
  network_name_regex = re.compile( r'/compute/v1/projects/[^/]+/([^/]+)/[^/]+/[^/]+/([^$]+)')
  if ( f"{network['network']}" == 'true'):
    print(  "auto-delete=yes", end=',')
  else:
    print(  "auto-delete=no", end=',')



def create_instances( config_file, delete_command, create_command, delete_disks, keep_disks):
  system = json.load( config_file)

  print( f"\n");

  if ( delete_command is True):
    # gcloud compute instances delete NAME
    print( f"gcloud compute instances delete {system['name']}", end=' ')

    # [--zone=ZONE]
    print( f"--zone='{system['zone']}'", end=' ')

    # [--delete-disks=DISK_TYPE [all|boot|data] ]
    print( f"--delete-disks='{delete_disks}'", end=' ')

    # [--keep-disks=DISK_TYPE [all|boot|data] ]
    print( f"--keep_disks='{keep_disks}'", end=' ')

    print("")

  if ( create_command is True):
    # gcloud compute instances create NAME
    print( f"gcloud compute instances create {system['name']}", end=' ')

    # [--accelerator=[count=COUNT],[type=TYPE]]
    # [--async]
    # [--no-boot-disk-auto-delete]
    # [--boot-disk-device-name=BOOT_DISK_DEVICE_NAME]
    # [--boot-disk-provisioned-iops=BOOT_DISK_PROVISIONED_IOPS]
    # [--boot-disk-provisioned-throughput=BOOT_DISK_PROVISIONED_THROUGHPUT]
    # [--boot-disk-size=BOOT_DISK_SIZE]
    # [--boot-disk-type=BOOT_DISK_TYPE]
    # [--can-ip-forward]
    # [--create-disk=[PROPERTY=VALUE,…]]
    # [--csek-key-file=FILE]

    # [--deletion-protection]
    print( f"--deletion-protection='{system['deletionProtection']}'", end=' ')

    # [--description=DESCRIPTION]
    print( f"--description='{system['description']}'", end=' ')

    for disk in system['disks']:
      diskOptions( disk)

    # [--enable-display-device]
    # [--[no-]enable-nested-virtualization]
    # [--[no-]enable-uefi-networking]
    # [--erase-windows-vss-signature]
    # [--external-ipv6-address=EXTERNAL_IPV6_ADDRESS]
    # [--external-ipv6-prefix-length=EXTERNAL_IPV6_PREFIX_LENGTH]
    # [--hostname=HOSTNAME]
    # [--instance-termination-action=INSTANCE_TERMINATION_ACTION]
    # [--internal-ipv6-address=INTERNAL_IPV6_ADDRESS]
    # [--internal-ipv6-prefix-length=INTERNAL_IPV6_PREFIX_LENGTH]
    # [--ipv6-network-tier=IPV6_NETWORK_TIER]
    # [--ipv6-public-ptr-domain=IPV6_PUBLIC_PTR_DOMAIN]
    # [--key-revocation-action-type=POLICY]
    # [--labels=[KEY=VALUE,…]]
    # [--local-ssd=[device-name=DEVICE-NAME],[interface=INTERFACE],[size=SIZE]]
    # [--local-ssd-recovery-timeout=LOCAL_SSD_RECOVERY_TIMEOUT]

    # [--machine-type=MACHINE_TYPE]
    machine_type = system['machineType'].rsplit('/', 1)
    print( f"--machine-type='{machine_type}'", end=' ')

    # [--maintenance-policy=MAINTENANCE_POLICY]

    # [--metadata=KEY=VALUE,[KEY=VALUE,…]]

    # [--metadata-from-file=KEY=LOCAL_FILE_PATH,[…]]

    # [--min-cpu-platform=PLATFORM default="AUTOMATIC"]
    # CPU platform selection is available only in selected zones.
    # Not available with Shared-Core, General-Purpose VMs
    # https://cloud.google.com/compute/docs/instances/specify-min-cpu-platform#limitations
    # https://cloud.google.com/compute/docs/machine-resource#shared-core-types
    if ( machine_type not in shared_core_general_purpose_machine_types):
      print( f"--min-cpu-platform='{system['cpuPlatform']}'", end=' ')

    # [--min-node-cpu=MIN_NODE_CPU]
    # [--network=NETWORK]
    # [--network-interface=[PROPERTY=VALUE,…]]
#    for network in system['networkInterfaces']:
#      networkOptions( network)

    # [--network-performance-configs=[PROPERTY=VALUE,…]]
    # [--network-tier=NETWORK_TIER]
    # [--node-project=NODE_PROJECT]
    # [--performance-monitoring-unit=PERFORMANCE_MONITORING_UNIT]
    # [--preemptible]
    # [--private-ipv6-google-access-type=PRIVATE_IPV6_GOOGLE_ACCESS_TYPE]
    # [--private-network-ip=PRIVATE_NETWORK_IP]
    # [--provisioning-model=PROVISIONING_MODEL]
    # [--no-require-csek-key-create]
    # [--resource-manager-tags=[KEY=VALUE,…]]
    # [--resource-policies=[RESOURCE_POLICY,…]]
    # [--no-restart-on-failure]
    # [--shielded-integrity-monitoring]
    # [--shielded-secure-boot]
    # [--shielded-vtpm]
    # [--source-instance-template=SOURCE_INSTANCE_TEMPLATE]
    # [--source-machine-image=SOURCE_MACHINE_IMAGE]
    # [--source-machine-image-csek-key-file=FILE]
    # [--stack-type=STACK_TYPE]
    # [--subnet=SUBNET]
    # [--tags=TAG,[TAG,…]]
    # [--threads-per-core=THREADS_PER_CORE]
    # [--visible-core-count=VISIBLE_CORE_COUNT]

    # [--zone=ZONE]
    print( f"--zone='{system['zone']}'", end=' ')

    # [--address=ADDRESS     | --no-address]
    # [--boot-disk-kms-key=BOOT_DISK_KMS_KEY : --boot-disk-kms-keyring=BOOT_DISK_KMS_KEYRING --boot-disk-kms-location=BOOT_DISK_KMS_LOCATION --boot-disk-kms-project=BOOT_DISK_KMS_PROJECT]
    # [--confidential-compute     | --confidential-compute-type=CONFIDENTIAL_COMPUTE_TYPE]
    # [--custom-cpu=CUSTOM_CPU --custom-memory=CUSTOM_MEMORY : --custom-extensions --custom-vm-type=CUSTOM_VM_TYPE]
    # [--image-family-scope=IMAGE_FAMILY_SCOPE --image-project=IMAGE_PROJECT --image=IMAGE     | --image-family=IMAGE_FAMILY     | --source-snapshot=SOURCE_SNAPSHOT]
    # [--instance-kms-key=INSTANCE_KMS_KEY : --instance-kms-keyring=INSTANCE_KMS_KEYRING --instance-kms-location=INSTANCE_KMS_LOCATION --instance-kms-project=INSTANCE_KMS_PROJECT]
    # [--node=NODE     | --node-affinity-file=NODE_AFFINITY_FILE     | --node-group=NODE_GROUP]
    # [--public-ptr     | --no-public-ptr]
    # [--public-ptr-domain=PUBLIC_PTR_DOMAIN     | --no-public-ptr-domain]
    # [--reservation=RESERVATION --reservation-affinity=RESERVATION_AFFINITY; default="any"]
    # [--scopes=[SCOPE,…]     | --no-scopes]
    # [--service-account=SERVICE_ACCOUNT     | --no-service-account]

    print("")


def main():
  arg_parser = argparse.ArgumentParser(
    prog='gcput-json2instances.py',
    description='Read exported GCP instances in json format,'
    'and print gcloud commands needed to recreate them.'
  )

  # Optional: Print delete command
  arg_parser.add_argument(
    '--deleteDiskType',
    required=False,
    dest='deleteDiskType',
    action='append',
    help="The types of disks to delete with instance deletion regardless of"
         "the disks' auto-delete configuration.  Must be one of [all|boot|data]"
  )

  # Optional: Print create command
  arg_parser.add_argument(
    '--keepDiskType',
    required=False,
    dest='keepDiskType',
    action='append',
    help="The types of disks to keep with instance deletion regardless of"
         "the disks' auto-delete configuration.  Must be one of [all|boot|data]"
  )

  # Optional: Print delete command
  arg_parser.add_argument(
    '-d',
    '--delete',
    required=False,
    dest='delete',
    action='store_true',
    help='Print "gcloud compute firewall-rules delete" command.'
  )

  # Optional: Print create command
  arg_parser.add_argument(
    '-c',
    '--create',
    required=False,
    dest='create',
    action='store_true',
    help='Print "gcloud compute firewall-rules create" command.'
  )

  # Import JSON files
  arg_parser.add_argument(
    'instances_json_config_file',
    help='JSON file containing instances rules to be recreated',
    type=argparse.FileType('r'), nargs='*', default=[sys.stdin]
  )

  args = arg_parser.parse_args()

  if ( args.delete is not True and args.create is not True):
    args.create = True

  for instances_config in args.instances_json_config_file:
    print( f"create_instances( {instances_config}, {args.delete}, {args.create}, {args.keepDiskType}, {args.deleteDiskType}")
    create_instances( instances_config, args.delete, args.create, args.keepDiskType, args.deleteDiskType)


if __name__ == '__main__':
  main()
