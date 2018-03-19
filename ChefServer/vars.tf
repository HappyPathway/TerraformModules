variable "private_subnet_id" {}
variable "public_subnet_id" {}

variable "instance_type" {
  default = "m4.large"
}

variable "key_name" {}

variable "chef_admin_user" {
  default = "admin"
}

variable "chef_admin_fname" {
  default = "Admin"
}

variable "chef_admin_lname" {
  default = "User"
}

variable "chef_admin_email" {
  default = "devops@happypathway.com"
}

variable "chef_org" {
  default = "devops"
}

variable "org_name" {
  default = "DevOps"
}

variable "domain" {
  default = "happypathway"
}

variable "server_name" {
  default = "chef"
}

variable "install_chef_manage" {
  default = true
}

variable "vpc_id" {}
