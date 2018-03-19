resource "aws_security_group" "bastion" {
  name   = "bastion"
  vpc_id = "${var.vpc_id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.ssh_access}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags {
    public_subnet_id  = "${var.public_subnet_id}"
    private_subnet_id = "${var.private_subnet_id}"
  }
}
