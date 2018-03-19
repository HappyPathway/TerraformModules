resource "aws_route53_zone" "default" {
  name   = "${var.domain}"
  vpc_id = "${aws_vpc.vpc.id}"
}
