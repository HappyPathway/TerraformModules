variable "vpc_name" {
  default = "terraform-vpc"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "route_table_name" {
  default = "terraform-route-table"
}

variable "domain" {}
