resource "aws_vpc" "vpc" {
  cidr_block = "${var.vpc_cidr}"
  tags {
    Name = "${var.vpc_name}"
  }
}

resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.vpc.id}"
}

resource "aws_route_table" "default" {
  vpc_id = "${aws_vpc.vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.default.id}"
  }

  tags {
    Name = "${var.route_table_name}"
  }
}

output "vpc_id" {
  value = "${aws_vpc.vpc.id}"
}

output "vpc_cidr" {
  value = "${var.vpc_cidr}"
}

output "route_table_id" {
  value = "${aws_route_table.default.id}"
}