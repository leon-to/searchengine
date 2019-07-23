import boto.ec2

conn = boto.ec2.connect_to_region(
    "us-east-1",
    aws_access_key_id='AKIAJPIDVSD2PW7AXOTQ',
    aws_secret_access_key='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')

addresses = conn.get_all_addresses()

for a in addresses:
    print a.public_ip, a.instance_id


