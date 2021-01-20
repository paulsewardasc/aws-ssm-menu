#!/usr/bin/python3

import boto3
import sys
import os
from pathlib import Path
import time
import json
from collections import defaultdict

def main():
  # Create ~/.ssm folder if it does not exist
  home = os.path.expanduser("~")
  if not os.path.exists(f'{home}/.ssm'):
      os.makedirs(f'{home}/.ssm')
      file1 = open(f'{home}/.ssm/ssm.config','w')
      print('regions=[eu-west-2, eu-west-1, us-east-1]', file=file1)
      print('profiles=[profile1,profile2]', file=file1)
      print('sshuser=ec2-user', file=file1)
      print('keyfile=~/.ssh/id_rsa', file=file1)
      file1.close()
      print(f'Now edit {home}/.ssm/ssm.config to meet your needs')
      sys.exit(0)
  
  home = str(Path.home())
  menu = []
  file1 = open(f'{home}/.ssm/ssm.config', 'r') 
  lines = file1.readlines() 
  profiles = []
  for line in lines:
    line = line.strip()
    if 'profiles' in line:
      profile = line[line.find("[")+1:line.find("]")]
      profiles = profile.split(',')
  
  #session = boto3.Session(region_name='us-east-1')
  #client = boto3.client('ec2')
  #regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
  regions = ['eu-west-3', 'eu-west-2', 'eu-west-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
  
  for profile in profiles:
    try:
      for region in regions:
        session = boto3.Session(profile_name=profile, region_name=region)
        try:
          ec2 = session.resource('ec2')
          running_instances = ec2.instances.filter(Filters=[{ 'Name': 'instance-state-name', 'Values': ['running']}])
          ec2info = defaultdict()
          for instance in running_instances:
            name = "blank"
            for tag in instance.tags:
              if tag['Key'] == 'Name':
                name = tag['Value']
            # Add instance info to a dictionary         
            ec2info[instance.id] = {
              'Name': name,
              'Type': instance.instance_type,
              'State': instance.state['Name'],
              'Private IP': instance.private_ip_address,
              'Public IP': instance.public_ip_address,
              'Launch Time': instance.launch_time,
              'Region' : region
            }
        except Exception as e:
          print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
          None 
        try:
          if len(ec2info) > 0:
            ssm = session.client('ssm')
            ssm_instances = [i['InstanceId'] for i in session.client('ssm').describe_instance_information()['InstanceInformationList']]
            if len(ssm_instances) > 0:
              for ssm_instance in ssm_instances:
                #ind = ec2info.index(ssm_instance)
                for instance_id, instance in ec2info.items():
                  #print(instance['Name'], instance_id, ssm_instance)
                  if instance_id == ssm_instance:
                    menu.append((f'{profile},{instance["Name"]},{instance_id},{instance["Private IP"]},{instance["Region"]}'))
              
        except Exception as e:
          #None 
          print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    except Exception as e:
      print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
      None  
  
  file2 = open(f'{home}/.ssm/ssm.csv', 'w') 
  print('Found: ')
  for menuitem in menu:
    print(f'{menuitem}', file=file2)
    print(f'{menuitem}')
  file2.close

if __name__ == "__main__":
    main()

