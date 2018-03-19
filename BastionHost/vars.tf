variable "private_subnet_id" {}
variable "public_subnet_id" {}
variable "vpc_id" {}
variable "ssh_access" {}

variable "instance_type" {
  default = "m1.large"
}

variable "key_name" {}
