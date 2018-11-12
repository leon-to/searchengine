import boto.ec2
import sys

conn = boto.ec2.connect_to_region(
    "us-east-1",
    aws_access_key_id='AKIAJPIDVSD2PW7AXOTQ',
    aws_secret_access_key='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')

reserve = conn.get_all_instances()
instances = [i for r in reserve for i in r.instances]
key_pairs = conn.get_all_key_pairs()
security_groups = conn.get_all_security_groups()
   
for i in instances:
    if i.id in sys.argv:
        print 'Terminate instance: ', i.id
        i.terminate()    


