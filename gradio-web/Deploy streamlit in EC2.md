# Deploy streamlit in EC2

### 1.Create EC2 instance

Network settings choose "Allow HTTP traffic from the internet"

### 2.Connect to EC2, install the following dependencies:

```
sudo yum update
sudo yum install nginx
sudo yum install tmux -y
sudo yum install python3-pip
pip3 install streamlit==1.27.2
pip3 install boto3
```

### 3.Create nginx profiles

```
cd /etc/nginx/conf.d
sudo touch streamlit.conf
sudo chmod 777 streamlit.conf
vi streamlit.conf
```

enter the template:

```
upstream ws-backend {
        server xxx.xxx.xxx.xxx:8501;
}

server {
    listen 80;
    server_name xxx.xxx.xxx.xxx;

    location / {
            
    proxy_pass http://ws-backend;

    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
    }
  }
```

Change the xxx.xxx.xxx.xxx to the EC2 private IP.


### 4. start nginx

```
sudo systemctl start nginx.service
```

### 5.Run streamlit ui stript

```
cd /home/ec2-user/guidance-for-custom-search-of-an-enterprise-knowledge-base-on-aws/gradio-web/
tmux
streamlit run xxxx.py
```

### 6.Open streamlit page

Enter the url in the webpage：http://<EC2 public IP>
