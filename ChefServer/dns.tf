data "aws_route53_zone" "selected" {
  name         = "${var.domain}"
  private_zone = false
  #vpc_id = "${var.vpc_id}"
}

resource "aws_route53_record" "service" {
  zone_id = "${data.aws_route53_zone.selected.zone_id}"
  name    = "${var.server_name}.${var.domain}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_instance.chef_server.public_ip}"]
}
