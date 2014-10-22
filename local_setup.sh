#!/bin/bash

echo "Adding security group rules"
nova --os-tenant-name=demo secgroup-add-rule default icmp -1 -1 0.0.0.0/0
nova --os-tenant-name=demo secgroup-add-rule default tcp 1 65535 0.0.0.0/0

#echo "Opening all ports in local firewall"
#sudo firewall-cmd --add-port=1-65535/tcp || echo "already all set"

echo "Adding keypair to Nova"
nova --os-tenant-name=demo keypair-add --pub_key ~/cloud_key.pub cloud_key
nova --os-tenant-name=demo --os-username=demo keypair-add --pub_key ~/cloud_key.pub cloud_key

echo "Adding Sahara endpoints"
S_EP="http://localhost:8386/v1.1/%(tenant_id)s"
S_ID=`keystone service-create --name sahara --type data_processing | awk '/id/ { print $4 }'`
keystone endpoint-create --region RegionOne --service $S_ID --publicurl $S_EP --internalurl $S_EP --adminurl $S_EP
