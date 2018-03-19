resource "aws_security_group" "admin" {
  name   = "${aws_subnet.subnet.id}-subnet-admin"
  vpc_id = "${var.vpc_id}"

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = -1
    self            = true
  }

  lifecycle {
    create_before_destroy = true
  }
}