#!/usr/bin/env python3
import os
import sys
import re
import argparse
from pprint import pprint
from simple_term_menu import TerminalMenu

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_searchstr():
    my_parser = argparse.ArgumentParser(description='SSM Menu: ssmmenu [search]') 
    my_parser.add_argument('search', nargs='*')
    my_parser.add_argument('--noprofile', action='store_true', help='dont use a profile, use the environmental variables')
    my_parser.add_argument('--show', action='store_true')
    my_parser.add_argument('--forward', nargs=2, help='localport destinationport')
    my_parser.add_argument('--key', nargs=1, help='path to the keyfile you want to use, this overides config')
    my_parser.add_argument('--user', nargs=1, help='username to use, this overides config')
    args = my_parser.parse_args()
    return args.search, args.show, args.forward, args.key, args.user, args.noprofile

def get_vars(home):
    file1 = open(f'{home}/.ssm/ssm.config','r')
    lines = file1.readlines()
    try:
      matches = matches = [s for s in lines if 'sshuser' in str(s)]   
      matches = matches[0].split('=') 
      sshuser = matches[1].strip()
    except:
      print("sshuser missing from ~/.ssm/ssm.config")
      sys.exit()
    try:
      matches = matches = [s for s in lines if 'keyfile' in str(s)]  
      matches = matches[0].split('=') 
      keyfile = matches[1].strip()
    except:
      print("keyfile missing from ~/.ssm/ssm.config")
      sys.exit()
    file1.close()
    return sshuser, keyfile

def get_lines(home):
    file2 = open(f'{home}/.ssm/ssm.csv','r')
    lines = file2.readlines()
    file2.close()
    lines=list(map(str.strip, lines))
    return lines

def show_menu(mlines, lines):
    menuitems = []
    for line in mlines:
      line = line.strip()
      fields = line.split(',')
      menuitems.append(f'{fields[0]}: {fields[1]} ({fields[2]}, {fields[3]}, {fields[4]})') 
    terminal_menu = TerminalMenu(menuitems)
    menu_entry_index = terminal_menu.show()
    if menu_entry_index is not None:
      foundline  = mlines[menu_entry_index]
      # Now find line in original index
      actual_index = lines.index(foundline)
      return actual_index
    else:
      return None

def searchforline(searchlist, lines):
    found_lines = []
    index = 0
    found_index = None
    menu_entry_index = None
    for line in lines:
      line = line.strip()
      for searchstr in searchlist:
        pattern = re.compile('(?i).*' + searchstr + '.*')
        if re.match(pattern, line):
          found_lines.append(line)
          found_index = index
      index += 1
    if len(found_lines) > 1:
      # Send both found lines and original lines, so we can find the right index
      menu_entry_index = show_menu(found_lines, lines)
    else:
      menu_entry_index = found_index
    return menu_entry_index 

def main():
    home = os.path.expanduser("~")
    sshuser, keyfile = get_vars(home)
    lines = get_lines(home)
    searchlist, showcommands, forwardcommand, altkey, altuser, noprofile = get_searchstr()
    if altuser is not None:
      sshuser = altuser[0]
    if altkey is not None:
      keyfile = os.path.expanduser(altkey[0])
    menu_entry_index = None
    # If no search list show all entries
    if len(searchlist) == 0:
      menu_entry_index = show_menu(lines,lines)
    else:
      # Show only matching entries
      menu_entry_index = searchforline(searchlist, lines)
    if menu_entry_index is not None:
      fields = lines[menu_entry_index].strip().split(',')
      id=fields[2].strip()
      ifo = f'-i {keyfile} -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
      if noprofile:
        pco = f'-o ProxyCommand="sh -c \'aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters \"portNumber=%p\" --region={fields[4]}\'"'
      else:
        pco = f'-o ProxyCommand="sh -c \'aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters \"portNumber=%p\" --profile={fields[0]} --region={fields[4]}\'"'
      if showcommands is False:
        if forwardcommand is None:
          try:
            clear = lambda: os.system('clear')
            clear()
          except:
            clear = lambda: os.system('cls')
            clear()
          print(f'ssh {ifo} {pco} {sshuser}@{id}')
          os.system(f'ssh {ifo} {pco} {sshuser}@{id}')
        else:
          lport = forwardcommand[0]
          dport = forwardcommand[1]
          if noprofile:
            pc = 'aws ssm start-session --target ' + id + ' --region=' + fields[4] + ' --document-name AWS-StartPortForwardingSession --parameters \'{"portNumber":["' + dport + '"],"localPortNumber":["' + lport + '"]}\''
          else:
            pc = 'aws ssm start-session --target ' + id + ' --profile=' + fields[0] + ' --region=' + fields[4] + ' --document-name AWS-StartPortForwardingSession --parameters \'{"portNumber":["' + dport + '"],"localPortNumber":["' + lport + '"]}\''
          print(f'{pc}')
          os.system(f'{pc}')
      else:
        print('Add the following to your ssh config (~/.ssh/config)\n')
        print(f'{bcolors.OKBLUE}host i-* mi-*')
        print(f'    IdentityFile {ifo}')
        print(f'    {pco}{bcolors.ENDC}\n')
        print(f'Then run:\n')
        print(f'{bcolors.OKBLUE}ssh {sshuser}@{id}{bcolors.ENDC}\n')
        
#GlobalKnownHostsFile=/dev/null
#UserKnownHostsFile=/dev/null
#StrictHostKeyChecking=no

if __name__ == "__main__":
    main()
