data "aws_acm_certificate" "service" {
  count = "${var.enable_ssl ? 1 : 0}"
  domain = "${var.domain}"
}
