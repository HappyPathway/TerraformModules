provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "chef_server" {
  key_name   = "${var.key_name}"
  public_key = "${file("~/.ssh/${var.key_name}.pub")}"
}

module "vpc" {
  source = "github.com/HappyPathway/VPC"
}

module "public_subnet" {
  source            = "github.com/HappyPathway/PublicSubnet"
  subnet_name       = "${var.company_name}-${var.org_name}-${var.service_name}-public"
  vpc_id            = "${module.vpc.vpc_id}"
  route_table_id    = "${module.vpc.route_table_id}"
  availability_zone = "us-east-1a"
}

module "private_subnet" {
  source            = "github.com/HappyPathway/PrivateSubnet"
  subnet_name       = "${var.company_name}-${var.org_name}-${var.service_name}-private"
  vpc_id            = "${module.vpc.vpc_id}"
  public_subnet_id  = "${module.public_subnet.subnet_id}"
  availability_zone = "us-east-1a"
}

module "Bastion" {
  source            = "github.com/HappyPathway/BastionHost"
  public_subnet_id  = "${module.public_subnet.subnet_id}"
  private_subnet_id = "${module.private_subnet.subnet_id}"
  vpc_id            = "${module.vpc.vpc_id}"
  ssh_access        = "0.0.0.0/0"
  key_name          = "${var.key_name}"
}

module "Chef" {
  source            = "github.com/HappyPathway/TF_ChefServer"
  public_subnet_id  = "${module.public_subnet.subnet_id}"
  private_subnet_id = "${module.private_subnet.subnet_id}"
  key_name          = "${var.key_name}"
  domain            = "ops.happypathway.com"
  vpc_id            = "${module.vpc.vpc_id}"
}

output "chef_host" {
  value = "${module.Chef.chef_host}"
}

output "chef_user" {
  value = "${module.Chef.chef_user}"
}

output "chef_password" {
  value = "${module.Chef.chef_password}"
}
