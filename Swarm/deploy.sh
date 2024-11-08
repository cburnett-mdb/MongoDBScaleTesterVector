#!/bin/bash

region="us-east-1"
ami="ami-0866a3c8686eaeeba" # Ubuntu
count="3"
instance_type="c5.12xlarge"
key_name="grabosky2024"
sg="sg-08abdf882f6667136"
vpc="vpc-52363036"
owner="chris.grabosky"
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