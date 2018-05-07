variable "service_port" {
  default = 8500
}

variable "service_healthcheck" {
  default = "ui"
}

variable "service_access" {
  default = "0.0.0.0/0"
}

variable "ssh_access" {
  default = "0.0.0.0/0"
}

variable "consul_access" {
  default = "0.0.0.0/0"
}

variable "cluster" {
  default = "dc1"
}

variable "instance_type" {
  default = "m4.large"
}

variable "key_name" {}

variable "min_size" {
  default = 1
}

variable "max_size" {
  default = 3
}

variable "high_cpu" {
  default = 85
}

variable "low_cpu" {
  default = 35
}

variable "default_cooldown" {
  default = 600
}

variable "public_subnet_id" {}
variable "private_subnet_id" {}
variable "vpc_id" {}

variable "service_healthcheck_healthy_threshold" {
  default = 2
}

variable "service_healthcheck_unhealthy_threshold" {
  default = 3
}

variable "service_healthcheck_timeout" {
  default = 3
}

variable "service_healthcheck_interval" {
  default = 30
}

variable "instance_protocol" {
  default = "http"
}

variable "cross_zone_load_balancing" {
  default = true
}

variable "connection_draining_timeout" {
  default = 400
}

variable "connection_draining" {
  default = true
}

variable "idle_timeout" {
  default = 400
}

variable "set_dns" {
  default = true
}

variable "enable_ssl" {
  default = true
}

variable "domain" {}