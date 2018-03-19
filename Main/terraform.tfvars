company_name="HappyPathway"
org_name="DevOps"
service_name="ops"

instance_type="m4.large"
key_name="hpw_devops"
subnet_cidr= "10.0.1.0/24"
vpc_cidr= "10.0.0.0/16"

service_name="frontend"
service_port=80
service_healthcheck="health"
service_access="0.0.0.0/0"

ssh_access="0.0.0.0/0"
region = "us-east-1"

key_name = "tfmodules"