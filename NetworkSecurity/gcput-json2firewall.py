#!/usr/bin/env python3
# vim: set ft=python tabstop=2 shiftwidth=2 expandtab :
#
# SPDX-FileCopyrightText: 2024 Shane Chambers <license@AustinLinux.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Input: json file containing firewall rules
# ie: gcloud compute firewall-rules list --format=json
#
# Expected output: gcloud compute firewall-rules create commands
# ie: gcloud compute firewall-rules create onprem-to-gcp
#     --description='Onprem access to GCP' \
#     --direction='INGRESS' \
#     --priority='1000' \
#     --network='https://www.googleapis.com/compute/v1/projects/' \
#               'gcp-project/global/networks/gcp-network' \
#     --destination-ranges='10.10.10.0/24,10.10.11.0/24' \
#     --source-ranges='10.1.1.0/24,10.1.2.0/24' \
#     --acction='ALLOW'
#     --rules='all'
#
#

import sys
import json
import argparse


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def create_firewall_rules( config_file, create_command, delete_command):
  firewall_data = json.load( config_file)

  for rule in firewall_data:

    if ( delete_command is True):
      # gcloud compute firewall-rules delete NAME
      print( f"gcloud compute firewall-rules delete {rule['name']}", end=' ')

      # [--network=NETWORK; default="default"]
      print( f"--network='{rule['network']}'", end=' ')

      print("")

    if ( create_command is True):
      # gcloud compute firewall-rules create NAME
      print( f"gcloud compute firewall-rules create {rule['name']}", end=' ')

      # [--description=DESCRIPTION]
      print( f"--description='{rule['description']}'", end=' ')

      # [--direction=DIRECTION]
      print( f"--direction='{rule['direction']}'", end=' ')

      # [--priority=PRIORITY]
      print( f"--priority='{rule['priority']}'", end=' ')

      # [--network=NETWORK; default="default"]
      print( f"--network='{rule['network']}'", end=' ')

      # [--disabled]
      try:
        if ( rule['disabled'] == 'True'):
          print( "--disabled", end=' ')
      except KeyError:
        print( "", end='')

      # [ --[no-]enable-logging] [--logging-metadata=LOGGING_METADATA] ]
      try:
        if ( rule[ 'logConfig']['enable'] == 'True'):
          print( "--enable-logging", end=' ')
      except KeyError:
        print( "", end='')

      # [--destination-ranges=CIDR_RANGE,[CIDR_RANGE,…]]
      try:
        if rule['destinationRanges']:
          ranges = []
          for dest_cidr in rule['destinationRanges']:
            ranges.append( f"{dest_cidr}")
          all_ranges = ','.join( ranges).replace( ",$", "")
          print( f"--destination-ranges='{all_ranges}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--source-ranges=CIDR_RANGE,[CIDR_RANGE,…]]
      try:
        if rule['sourceRanges']:
          ranges = []
          for source_cidr in rule['sourceRanges']:
            ranges.append( f"{source_cidr}")
          all_ranges = ','.join( ranges).replace( ",$", "")
          print( f"--source-ranges='{all_ranges}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--source-service-accounts=EMAIL,[EMAIL,…]]
      try:
        if rule['sourceServiceAccounts']:
          emails = []
          for source_email in rule['sourceServiceAccounts']:
            emails.append( f"{source_email}")
          all_emails = ','.join( emails).replace( ",$", "")
          print( f"--source-service-accounts='{all_emails}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--target-service-accounts=EMAIL,[EMAIL,…]]
      try:
        if rule['targetServiceAccounts']:
          emails = []
          for target_email in rule['targetServiceAccounts']:
            emails.append( f"{target_email}")
          all_emails = ','.join( emails).replace( ",$", "")
          print( f"--target-service-accounts='{all_emails}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--source-tags=EMAIL,[EMAIL,…]]
      try:
        if rule['sourceTags']:
          tags = []
          for source_tag in rule['sourceTags']:
            tags.append( f"{source_tag}")
          all_tags = ','.join( tags).replace( ",$", "")
          print( f"--source-tags='{all_tags}'", end=' ')
      except KeyError:
        print( "", end='')

      # [--target-tags=EMAIL,[EMAIL,…]]
      try:
        if rule['targetTags']:
          tags = []
          for target_tag in rule['targetTags']:
            tags.append( f"{target_tag}")
          all_tags = ','.join( tags).replace( ",$", "")
          print( f"--target-tags='{all_tags}'", end=' ')
      except KeyError:
        print( "", end='')

      # [ --action=ALLOW --rules=PROTOCOL[:PORT[-PORT]],[…]]
      try:
        if rule['allowed']:
          print( "--acction='ALLOW'", end=' ')
          rules = []
          for allowed in rule['allowed']:
            if ( allowed['IPProtocol'] == 'tcp' or
                 allowed['IPProtocol'] == 'udp'):
              for port in allowed['ports']:
                rules.append( f"{allowed['IPProtocol']}:{port}")
            else:
                rules.append( f"{allowed['IPProtocol']}")
          all_rules = ','.join( rules).replace( ",$", "")
          print( f"--rules='{all_rules}'", end=' ')
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
    prog='gcput-json2firewall.py',
    description='Read exported GCP firewall rules in json format,'
    'and print gcloud commands needed to recreate the rules.'
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
    'firewall_json_config_file',
    help='JSON file containing Firewall rules to be recreated',
    type=argparse.FileType('r'), nargs='*', default=[sys.stdin]
  )

  args = arg_parser.parse_args()

  if ( args.delete is not True and args.create is not True):
    args.create = True

  for firewall_config in args.firewall_json_config_file:
    create_firewall_rules( firewall_config, args.create, args.delete)


if __name__ == '__main__':
  main()
