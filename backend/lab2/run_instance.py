import boto.ec2

# open connection to ec2
conn = boto.ec2.connect_to_region(
    "us-east-1",
    aws_access_key_id='AKIAJPIDVSD2PW7AXOTQ',
    aws_secret_access_key='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')

# run instance
reservation = conn.run_instances(
    image_id="ami-9aaa1cf2",
    instance_type="t2.micro",
    key_name="aws_key",
    security_groups=["csc326-group25"]
)

# get instance
inst = reservation.instances[0]

# update instance info
inst.update()

# print inst info
print inst.id, inst.groups[0], inst.state, inst.ip_address


