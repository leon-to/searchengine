import boto.ec2
import sys

# associate static ip address with inst id
#
# @param address_str: static ip address string (not object)
# @param inst_id: instance id

address_str = sys.argv[1]
inst_id = sys.argv[2]

# open connection to ec2
conn = boto.ec2.connect_to_region(
    "us-east-1",
    aws_access_key_id='AKIAJPIDVSD2PW7AXOTQ',
    aws_secret_access_key='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'
)

# retrieve list of available static ip addresses
addresses = conn.get_all_addresses()

# get address strs
address_str_list = [address.public_ip for address in addresses] 

# error out 
assert (address_str in address_str_list)

# get the matched address object
for a in addresses:
    if (a.public_ip == address_str):
        address = a
        break

# associate the address with inst id
address.associate(instance_id=inst_id)

print address.public_ip, address.domain, address.instance_id
