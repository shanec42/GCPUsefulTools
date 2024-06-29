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

  if ( args.delete is not True and args.create is not True):
    args.create = True

  for instances_config in args.instances_json_config_file:
    create_instances( instances_config, args.create, args.delete)


if __name__ == '__main__':
  main()
