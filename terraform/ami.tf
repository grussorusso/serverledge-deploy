data "aws_ami" "amazonlinux_edge" {
  most_recent = true

  filter {
    name = "name"
    values = ["amzn2-ami-hvm-*-x86_64-ebs"]
  }
  owners = ["amazon"]
}
data "aws_ami" "amazonlinux_cloud" {
  most_recent = true
  provider = aws.cloud

  filter {
    name = "name"
    values = ["amzn2-ami-hvm-*-x86_64-ebs"]
  }
  owners = ["amazon"]
}
