#!/bin/bash

region="us-east-1"
ami="ami-0866a3c8686eaeeba" # Ubuntu
count="3"
instance_type="c5.12xlarge"
key_name="cburnett2024"
sg="sg-0ebb8820bd1373389"
vpc="vpc-52363036"
owner="charles.burnett"
purpose="opportunity"
expireon="2024-12-01"
name="locusttest"

aws ec2 run-instances \
    --image-id ${ami} \
    --count ${count} \
    --instance-type ${instance_type} \
    --key-name ${key_name} \
    --security-group-ids ${sg}\
    --tag-specifications "ResourceType=instance,Tags=[{Key=owner,Value=$owner},{Key=purpose,Value=$purpose},{Key=expire-on,Value=$expireon},{Key=Name,Value=$name}]"