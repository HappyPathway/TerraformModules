data "aws_ami" "service_ami" {
  filter {
    name   = "state"
    values = ["available"]
  }

  filter {
    name   = "tag:service"
    values = ["consul"]
  }

  filter {
    name   = "tag:cluster"
    values = ["${var.cluster}"]
  }

  most_recent = true
}
