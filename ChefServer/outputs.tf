output "chef_host" {
  value = "${var.server_name}.${var.domain}"
}

output "chef_user" {
  value = "${var.chef_admin_user}"
}

output "chef_password" {
  value = "${random_string.password.result}"
}