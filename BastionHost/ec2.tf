data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

data "aws_subnet" "private_subnet" {
  id = "${var.private_subnet_id}"
}

resource "aws_instance" "bastion" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "${var.instance_type}"
  availability_zone = "${data.aws_subnet.private_subnet.availability_zone}"
  subnet_id = "${var.public_subnet_id}"
  security_groups = ["${aws_security_group.bastion.id}"]
  key_name                    = "${var.key_name}"
  tags {
    Name           = "BastionHost"
    private_subnet = "${var.private_subnet_id}"
    public_subnet  = "${var.public_subnet_id}"
  }
}
