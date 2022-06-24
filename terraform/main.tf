variable "edge_region" {
	type = string
}
variable "edge_instance_count" {
	type = number
}
variable "cloud_region" {
	type = string
}
variable "cloud_instance_count" {
	type = number
}

# The default provider configuration; resources that begin with `aws_` will use
# it as the default, and it can be referenced as `aws`.
provider "aws" {
  region = var.edge_region
}

# Additional provider configuration for Cloud region; resources can
# reference this as `aws.cloud`.
provider "aws" {
  alias  = "cloud"
  region = var.cloud_region
}

variable "aws_key_name" {
	type = string
}

variable "edge_instance_type" {
	type = string
}

variable "cloud_instance_type" {
	type = string
}


data "aws_vpc" "default" {
  default = true
}

data "aws_vpc" "defaultCloud" {
  provider = aws.cloud
  default = true
}

resource "aws_security_group" "edge-sg" {
  name        = "edge-sg"
  description = "Allow SSH and HTTP inbound traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "HTTP Serverledge"
    from_port        = 1323
    to_port          = 1323
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "UDP Serverledge"
    from_port        = 9876
    to_port          = 9876
    protocol         = "udp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

}

resource "aws_security_group" "cloud-sg" {
  name        = "cloud-sg"
  provider = aws.cloud
  description = "Allow SSH and HTTP inbound traffic"
  vpc_id      = data.aws_vpc.defaultCloud.id

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "etcd"
    from_port        = 2379
    to_port          = 2379
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "HTTP Serverledge"
    from_port        = 1323
    to_port          = 1324
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "UDP Serverledge"
    from_port        = 9876
    to_port          = 9876
    protocol         = "udp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

}


resource "aws_instance" "edge" {
  count         = var.edge_instance_count
  ami           = data.aws_ami.amazonlinux_edge.id
  instance_type = var.edge_instance_type
  key_name = var.aws_key_name
  security_groups = [aws_security_group.edge-sg.name]

  tags = {
    Name = "Edge"
  }
}

resource "aws_instance" "cloud" {
  count = var.cloud_instance_count
  provider = aws.cloud
  ami           = data.aws_ami.amazonlinux_cloud.id
  instance_type = var.cloud_instance_type
  key_name = var.aws_key_name
  security_groups = [aws_security_group.cloud-sg.name]

  tags = {
    Name = "Cloud"
  }
}


