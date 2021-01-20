# An AWS SSH Menu

### If you already use AWS Session Manager across multiple accounts this might be if use to you

This is a simple menu to allow you to use AWS Session Manager to SSH into servers using "ssh"

The script SSM (ssm) searches through all your accounts you have set up and all regions you set for EC2 instances accessible by AWS Session Manager (you need the correct permissions) and stores the instances in a csv file.

The script SSMMENU (ssmmenu) displays those instances and allows you to select the one you want to access using SSH and AWS Sesssion Manager as a proxy.

SSMMENU allows for quick access and filtering:

e.g. 

* `ssmmenu i-0bc16bd2c0ed` : will ssh straight to the instance instead of showing a menu
* `ssmmenu web` : will show all instances with the name containing `web`
* `ssmmenu prod.*web` will show all production web servers matching the regex of `.*prod.*web.*`
* `sshmenu --show` will not run the ssh command but show you the configuration needed to add to you `~/.ssh/config` so that other programs e.g. scp can use
* `sshmenu --forward 8080 80` will forward local port 8080 to port 80 on the EC2 instance so to can access the website from localhost:8080
* `sshmenu --forward 2222 22` will forward local port 2222 to port 22 on the EC2 instance so to can access port 22 on the EC2 using localhost:2222 (e.g. `ssh -i awsssm.pem ec2-user@localhost -p 2222`)

Note:

You need to have a private key that has access to the instance you want to ssh to.

e.g.

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -f $HOME/.ssh/aws-ssm
```

Then copy the .pub file onto the EC2 instance using some other method, e.g. use SSM Console access

It would be best to run SSM every so often but it is not possible to run it before creating the menu as it takes too long

## Installation
Requires:

* python3
* pip3

Pre-Requisites:

```bash
python3 -m pip install boto3
python3 -m pip install collections-extended
python3 -m pip install pathlib
python3 -m pip install simple_term_menu
```

Install:

* Download the git contents

```bash
git clone git@github.com:paulsewardasc/aws-ssm-menu.git
```

* Add the profiles to your ~/.aws/credentials file

* Run the following

```bash
cp ./ssm-menu/ssm-menu/ssm.py ~/.local/bin/ssm
chmod +x ~/.local/bin/ssm
cp ./ssm-menu/ssm-menu/ssmmenu.py ~/.local/bin/ssmmenu
chmod +x ~/.local/bin/ssmmenu
ssm
```
* Edit the ~/.ssm/ssm.config to match the profiles you want to use in your ~/.aws/credentials file and then run ssm again to populate the csv file
```bash
ssm
```

## Update
```bash
cd ./aws-ssm-menu
git pull
cp ./ssm-menu/ssm.py ~/.local/bin/ssm
cp ./ssm-menu/ssmmenu.py ~/.local/bin/ssmmenu
```


## Uninstall

```bash
rm ~/.local/bin/ssm
rm ~/.local/bin/ssmmenu
rm -fr ~/.ssm
```

