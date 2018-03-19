data "aws_security_group" "admin" {
  name = "${var.private_subnet_id}-subnet-admin"
}

resource "aws_network_interface" "private" {
  subnet_id       = "${var.private_subnet_id}"
  security_groups = ["${data.aws_security_group.admin.id}"]

  attachment {
    instance     = "${aws_instance.chef_server.id}"
    device_index = 1
  }
}