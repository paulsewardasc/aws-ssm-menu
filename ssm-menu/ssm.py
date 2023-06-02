#!/usr/bin/python3

import boto3
import sys
import os
from pathlib import Path
import time
import json
from collections import defaultdict
import datetime

version = '1.1'

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


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
  regions = ['eu-west-3', 'eu-west-2', 'eu-west-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
  profiles = []
  for line in lines:
    line = line.strip()
    if 'profiles' in line:
      profile = line[line.find("[")+1:line.find("]")]
      profiles = profile.split(',')
    if 'regions' in line:
      regions = line[line.find("[")+1:line.find("]")]
      regions = regions.replace(' ','')
      regions = regions.split(',')
  
  #session = boto3.Session(region_name='us-east-1')
  #client = boto3.client('ec2')
  #regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
 
  for profile in profiles:
    try:
      for region in regions:
        session = boto3.Session(profile_name=profile, region_name=region)
        try:
          ec2 = session.client('ec2')
          ssm = session.client('ssm')
          ssm_instance_store = [] 
          ssm_instances = ssm.describe_instance_information()
          for ssm_instance in ssm_instances['InstanceInformationList']:
            ssm_instance_store.append(ssm_instance)
          while 'NextToken' in ssm_instances:
            nextToken = ssm_instances['NextToken']
            ssm_instances = ssm.describe_instance_information(NextToken=nextToken)
            for ssm_instance in ssm_instances['InstanceInformationList']:
              ssm_instance_store.append(ssm_instance)
    
          ec2info = defaultdict()
          #print(json.dumps(ssm_instances, indent=2, default=datetime_handler))
          #if region == 'us-east-1':
          #  sys.exit()
          for instance in ssm_instance_store:
            instanceId = instance['InstanceId']
            #aws ssm describe-instance-information --instance-information-filter-list key=InstanceIds,valueSet=mi-01a6c52fd727e05a8 --profile=asc-infrastructure --region=eu-west-2
            name = "blank"
            if instanceId.startswith('i-'):
              instance_details = ec2.describe_instances(InstanceIds=[instanceId])['Reservations'][0]['Instances'][0]
              try:
                if instance_details['Tags']:
                  for tag in instance_details['Tags']:
                    if tag['Key'] == 'Name':
                      name = tag['Value']
              except:
                None
            else:
              filter={'key': 'InstanceIds', 'valueSet': [instanceId]}
              instance_details = ssm.describe_instance_information(InstanceInformationFilterList=[filter])['InstanceInformationList'][0]
              #print(json.dumps(instance_details, indent=2, default=datetime_handler))
              #sys.exit()
              try:
                if instance_details['Name']:
                  name = instance_details['Name']
              except:
                None
            try:
              publicIp = instance_details['PublicIpAddress']
            except:
              publicIp = ''
            try:
              privateIp = instance_details['NetworkInterfaces'][0]['PrivateIpAddress']
            except:
              privateIp = ''
            if instanceId.startswith('i-'): 
              ec2info[instanceId] = {
                'Name': name,
                'Type': instance_details['InstanceType'],
                'State': instance_details['State']['Name'],
                'Private IP': privateIp,
                'Public IP': publicIp,
                'Region' : region
              }
            else:
              ec2info[instanceId] = {
                'Name': name,
                'Type': 'XXX',
                'State': instance_details['PingStatus'],
                'Private IP': instance_details['IPAddress'],
                'Public IP': publicIp,
                'Region' : region
              }
        except Exception as e:
          print('Error on line [{}] {}'.format(profile,sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
          sys.exit()
          None 
        try:
          if len(ec2info) > 0:
            #ssm = session.client('ssm')
            #ssm_instances = [i['InstanceId'] for i in session.client('ssm').describe_instance_information()['InstanceInformationList']]
            if len(ssm_instance_store) > 0:
              for ssm_instance in ssm_instance_store:
                instanceId = ssm_instance['InstanceId'] 
                #ind = ec2info.index(ssm_instance)
                for instance_id, instance in ec2info.items():
                  #print(instance['Name'], instance_id, ssm_instance)
                  if instance_id == instanceId:
                    menu.append((f'{profile},{instance["Name"]},{instance_id},{instance["Private IP"]},{instance["Region"]}'))
              
        except Exception as e:
          #None 
          print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    except Exception as e:
      print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
      None  
  
  file2 = open(f'{home}/.ssm/ssm.csv', 'w') 
  print(f'SSM Version: {version}')
  print('Found the following EC2s: \n')
  for menuitem in menu:
    print(f'{menuitem}', file=file2)
    print(f'{menuitem}')
  file2.close

if __name__ == "__main__":
    main()

