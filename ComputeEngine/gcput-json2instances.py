#!/usr/bin/env python3
# vim: set ft=python tabstop=2 shiftwidth=2 expandtab :
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

import sys
import json
import argparse

shared_core_general_purpose_machine_types = [
  'e2-micro',
  'e2-small',
  'e2-medium',
  'f1-micro',
  'g1-small'
]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def create_instances( config_file, create_command, delete_command, delete_disks, keep_disks):
  instance_data = json.load( config_file)

  for system in instance_data:

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
      # [--description=DESCRIPTION]
      # [--disk=[auto-delete=AUTO-DELETE],[boot=BOOT],[device-name=DEVICE-NAME],[force-attach=FORCE-ATTACH],[mode=MODE],[name=NAME],[scope=SCOPE]]
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

      # [--description=DESCRIPTION]
      print( f"--description='{system['description']}'", end=' ')

      # [--direction=DIRECTION]
      print( f"--direction='{system['direction']}'", end=' ')

      # [--priority=PRIORITY]
      print( f"--priority='{system['priority']}'", end=' ')

      # [--network=NETWORK; default="default"]
      print( f"--network='{system['network']}'", end=' ')

      # [--disabled]
      try:
        if ( system['disabled'] == 'True'):
          print( "--disabled", end=' ')
      except KeyError:
        print( "", end='')

      # [ --[no-]enable-logging] [--logging-metadata=LOGGING_METADATA] ]
      try:
        if ( system[ 'logConfig']['enable'] == 'True'):
          print( "--enable-logging", end=' ')
      except KeyError:
        print( "", end='')

      # [--destination-ranges=CIDR_RANGE,[CIDR_RANGE,…]]
      try:
        if system['destinationRanges']:
          ranges = []
          for dest_cidr in system['destinationRanges']:
            ranges.append( f"{dest_cidr}")
          all_ranges = ','.join( ranges).replace( ",$", "")
          print( f"--destination-ranges='{all_ranges}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--source-ranges=CIDR_RANGE,[CIDR_RANGE,…]]
      try:
        if system['sourceRanges']:
          ranges = []
          for source_cidr in system['sourceRanges']:
            ranges.append( f"{source_cidr}")
          all_ranges = ','.join( ranges).replace( ",$", "")
          print( f"--source-ranges='{all_ranges}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--source-service-accounts=EMAIL,[EMAIL,…]]
      try:
        if system['sourceServiceAccounts']:
          emails = []
          for source_email in system['sourceServiceAccounts']:
            emails.append( f"{source_email}")
          all_emails = ','.join( emails).replace( ",$", "")
          print( f"--source-service-accounts='{all_emails}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--target-service-accounts=EMAIL,[EMAIL,…]]
      try:
        if system['targetServiceAccounts']:
          emails = []
          for target_email in system['targetServiceAccounts']:
            emails.append( f"{target_email}")
          all_emails = ','.join( emails).replace( ",$", "")
          print( f"--target-service-accounts='{all_emails}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--source-tags=EMAIL,[EMAIL,…]]
      try:
        if system['sourceTags']:
          tags = []
          for source_tag in system['sourceTags']:
            tags.append( f"{source_tag}")
          all_tags = ','.join( tags).replace( ",$", "")
          print( f"--source-tags='{all_tags}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--target-tags=EMAIL,[EMAIL,…]]
      try:
        if system['targetTags']:
          tags = []
          for target_tag in system['targetTags']:
            tags.append( f"{target_tag}")
          all_tags = ','.join( tags).replace( ",$", "")
          print( f"--target-tags='{all_tags}'", end=' ')
      except KeyError:
        print( "", end='')

      # [ --action=DENY --rules=PROTOCOL[:PORT[-PORT]],[…]]
      try:
        if rule['denied']:
          print( "--action='DENY'", end=' ')
          rules = []
          for denied in rule['denied']:
            if ( denied['IPProtocol'] == 'tcp' or
                 denied['IPProtocol'] == 'udp'):
              for port in denied['ports']:
                rules.append( f"{denied['IPProtocol']}:{port}")
            else:
                rules.append( f"{denied['IPProtocol']}")
          all_rules = ','.join( rules).replace( ",$", "")
          print( f"--rules='{all_rules}'", end=' ')
      except KeyError:
        print( "", end='')

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
    '--createDiskType',
    required=False,
    dest='createDiskType',
    action='append',
    help="The types of disks to keep with instance deletion regardless of"
         "the disks' auto-delete configuration.  Must be one of [all|boot|data]"
  )

  # Import JSON files
  arg_parser.add_argument(
    'instances_json_config_file',
    help='JSON file containing instances rules to be recreated',
    type=argparse.FileType('r'), nargs='*', default=[sys.stdin]
  )

  args = arg_parser.parse_args()

#  if ( args.delete is not True and args.create is not True):
#    args.create = True

  for instances_config in args.instances_json_config_file:
    create_instances( instances_config, args.create, args.delete)


if __name__ == '__main__':
  main()
