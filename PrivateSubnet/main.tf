resource "aws_subnet" "subnet" {
  vpc_id                  = "${var.vpc_id}"
  cidr_block              = "${var.subnet_cidr}"
  map_public_ip_on_launch = false
  availability_zone       = "${var.availability_zone}"

  tags {
    Name = "${var.subnet_name}"
  }
}

output "subnet_id" {
  value = "${aws_subnet.subnet.id}"
}

output "subnet_cidr" {
  value = "${var.subnet_cidr}"
}
