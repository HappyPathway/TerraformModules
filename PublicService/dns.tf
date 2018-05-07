data "aws_route53_zone" "selected" {
  count = "${var.set_dns ? 1 : 0}"
  name         = "${var.domain}"
  private_zone = false

  # vpc_id = "${var.vpc_id}"
}

resource "aws_route53_record" "service" {
  count = "${var.set_dns ? 1 : 0}"
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "${var.service_name}.${var.domain}"
  type    = "CNAME"
  ttl     = "300"
  records = ["${aws_elb.service.dns_name}"]
}
