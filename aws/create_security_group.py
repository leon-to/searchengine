import boto.ec2

conn = boto.ec2.connect_to_region(
    "us-east-1",
    aws_access_key_id='AKIAJPIDVSD2PW7AXOTQ',
    aws_secret_access_key='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')

group = conn.create_security_group("csc326-group25", "1st security group")
group.authorize("icmp", -1, -1, "0.0.0.0/0")
group.authorize("tcp", 22, 22, "0.0.0.0/0")
group.authorize("tcp", 80, 80, "0.0.0.0/0")


