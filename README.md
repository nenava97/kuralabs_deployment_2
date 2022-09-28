# Deployment 2 Kura Labs Nicole Navarrete 09.27.22

## Purpose: Set up a CI/CD pipeline using a GitHub repository with a url-shortener app code which is then built out and tested with AWS CLI on a Jenkins EC2 and finally deployed from Elastic Beanstalk CLI

<img width="946" alt="Screen Shot 2022-09-27 at 11 49 34 PM" src="https://user-images.githubusercontent.com/108698688/192686243-3f75fdc7-fae7-40a0-a262-92634cf50d8b.png">

### Create  AWS EC2 and set up dependencies needed for Jenkins

1. Create an EC2 on AWS with the following configurations:
- ubuntu Amazon Machine Image
- t2.micro free tier eligible instance type
- create and download a new key pair on VM if don’t already have one (RSA key pair type and .pem private key file format ex key.pem),
- security groups (ssh, 22, 0.0.0.0/0) (HTTPS, 80, 0.0.0.0/0) (HTTPS, 8080, 0.0.0.0/0),
 
2. Log into EC2
In VM terminal make sure you are in the directory where your EC2 private key .pem is 
Make key readable to just you
```
$ chmod 400 key.pem
```
Find IP4 address of EC2 in AWS under EC2 dashboard and login
```
$ ssh -i key.pem ubuntu@<<EC2PublicIPV4address>>
```
Confirm you’re logged into EC2 in VM terminal by looking at user prompt 

3. Install unzip and 
```
$ sudo apt install unzip
```
4. Install python and pip
```
$ sudo apt install python3
$ sudo pip install python3-venv
```
5. Install Java
```
$ sudo apt update
$ sudo apt install openjdk-11-jre
$ java -version
```
6. Add jenkins user on EC2 to sudoers file 
```
$ sudo nano /etc/sudoers
```
<img width="560" alt="Screen Shot 2022-09-27 at 11 51 10 PM" src="https://user-images.githubusercontent.com/108698688/192686295-e1f0c8c5-a376-47aa-99a6-5288bd87d429.png">

### Install Jenkins on an EC2

7. Followed Jenkins documentation on how to install jenkins in Linux system (https://www.jenkins.io/doc/book/installing/linux/#debianubuntu )
```
$ curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \ /usr/share/keyrings/jenkins-keyring.asc > /dev/null
$ echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \ https://pkg.jenkins.io/debian-stable binary/ | sudo tee \ /etc/apt/sources.list.d/jenkins.list > /dev/null
$sudo apt-get update
$sudo apt-get install jenkins
```

### Activate the Jenkins user on the EC2

8. Start Jenkins 
```
$sudo systemctl start jenkins
$ sudo systemctl status jenkins
```
9. Change Jenkins password 
```
$sudo passwd jenkins
$sudo su - jenkins -s /bin/bash
```

### Create a Jenkins user in your AWS account

10. In IAM dashboard click on Users under Access Management and add a new user with the following configurations:
- Access key - Programmatic Access
- Set permissions, click on attach existing policies directly and check off Administrator Access
- Create user and make sure to copy and save Access Key ID and Secret Access Key made

## Install AWS Command Line Interface (AWS CLI) on the Jenkins EC2 and configure

11. Install AWS CLI tool to manage AWS services
```
$ curl
"https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
$ unzip awscliv2.zip
$ sudo ./aws/install
$ aws --version 
$ sudo su - jenkins -s /bin/bash 
$ aws configure 
```
For configuration
Access Key ID 
Secret Access Key 
Region us-east-1
Output format: json 

### Install EB CLI in the Jenkins EC2 user

12. Followed AWS Elastic Beanstalk documentation on how to manually install the EB CLI (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install-advanced.html)
```
$ pip install awsebcli --upgrade --user 
$ eb --version
```

<img width="1020" alt="Screen Shot 2022-09-27 at 11 51 33 PM" src="https://user-images.githubusercontent.com/108698688/192686334-cfb9623c-9549-45c0-8ffd-8fdde956c5f6.png">

Take note of the LOCAL_PATH where scripts are installed in so can add to $PATH
```
$ nano .bashrc
```

<img width="906" alt="Screen Shot 2022-09-27 at 11 51 41 PM" src="https://user-images.githubusercontent.com/108698688/192686358-30244476-b9e1-4adb-bde2-6116da8e5054.png">


Load profile script with the export command in current session
```
$ source ./.bashrc
```

### Connect GitHub to Jenkins Server

13. Fork repository https://github.com/kura-labs-org/kuralabs_deployment_2 
14. Create personal access token in GitHub
- Click on account settings 
- go to Developer Settings all the way at the bottom of left-side box
- click Personal access tokens and press generate new tokens
- select scopes repo and admin:repo_hook
- Copy token to use in next step

### Update Jenkinsfile and test_app.py in GitHub forked Repo

15. Commit following changes to deployment stage in Jenkinsfile
```
pipeline {
  agent any
   stages {
    stage ('Build') {
      steps {
        sh '''#!/bin/bash
        python3 -m venv test3
        source test3/bin/activate
        pip install pip --upgrade
        pip install -r requirements.txt
        export FLASK_APP=application
        flask run &
        '''
     }
   }
    stage ('test') {
      steps {
        sh '''#!/bin/bash
        source test3/bin/activate
        py.test --verbose --junit-xml test-reports/results.xml
        ''' 
      }
    
      post{
        always {
          junit 'test-reports/results.xml'
        }
       
      }
    }
    stage ('Deploy') {
     steps {
      sh '/var/lib/jenkins/.local/bin/eb deploy url-shortner-dev2'
    }
   }   
  }
 }
```
16. Commit update test in test_app.py
```
from application import app
#test
def test_home_page():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_home_page():
    response = app.test_client().post('/')
    assert response.status_code == 405
```

### Create a multibranch build

17. Configure Jenkins
- Open browser and enter http:\\<<EC2PublicIPv4address>>:8080
- Create Jenkins profile
- In Jenkins Dashboard 
- Add New Item
- Enter item name (ex url-shortener) and select Multibranch Pipeline
- Enter display name (ex Build Flask) and Description (ex CI/CD pipeline deployment 2)
- Add Branch Source as GitHub
- Add Jenkins 
- Enter GitHub username and paste access token as password
- Enter forked repository url and validate 
- Ensure Build Configuration says Jenkinsfile
- Apply and Save
- Select Scan repository if build doesn’t automatically start creating

## Deploy application from Elastic Beanstalk CLI

18. Configure project directory
```
$sudo su - jenkins -s /bin/bash
$cd /var/workspace/url-shortner/
$eb init
```
Follow configuration options in screenshots below

 <img width="484" alt="Screen Shot 2022-09-27 at 11 52 17 PM" src="https://user-images.githubusercontent.com/108698688/192686401-bdecd28e-0942-4f2a-a0b5-42c6fdf941c6.png">

```
$eb create
```

 <img width="883" alt="Screen Shot 2022-09-27 at 11 52 45 PM" src="https://user-images.githubusercontent.com/108698688/192686424-e6d1189a-ab77-4219-98bb-385ae630f6c0.png">
 
19. Test environment
Click on url AWS created for your environment and make sure the web page opens without error

<img width="823" alt="Screen Shot 2022-09-27 at 11 52 58 PM" src="https://user-images.githubusercontent.com/108698688/192686459-b11fa9a6-fcf4-43f7-a289-ad64cc475cbd.png">

## Errors

1. Permissions
In step 11 got errors that jenkins user was not a sudoer, and therefore couldn’t install or run 
 
 <img width="515" alt="Screen Shot 2022-09-27 at 11 53 07 PM" src="https://user-images.githubusercontent.com/108698688/192686495-a8796b2d-b5d7-4cb1-8dde-6466bd078c4b.png">

Had to exit sudo user and edit sudoer file as in step 6
 
 <img width="439" alt="Screen Shot 2022-09-27 at 11 53 15 PM" src="https://user-images.githubusercontent.com/108698688/192686593-e6130922-2de5-40cf-89bc-cce40779c7a2.png">

2. Dependencies

<img width="672" alt="Screen Shot 2022-09-27 at 11 53 25 PM" src="https://user-images.githubusercontent.com/108698688/192686643-142a1389-73c4-4205-8280-15c5786b7b7a.png">

When made first build of application got errors that the python test couldn’t run 
Had to install python as did in step 4
 
<img width="618" alt="Screen Shot 2022-09-27 at 11 53 36 PM" src="https://user-images.githubusercontent.com/108698688/192686700-1142c6f6-a496-4b76-91de-d89bc0793153.png">

3. PATH error
Path for eb couldn’t be found when tried to run deployment after updating Jenkinsfile and test_app.py in step 15
 
<img width="654" alt="Screen Shot 2022-09-27 at 11 53 46 PM" src="https://user-images.githubusercontent.com/108698688/192686740-c1fa1ac0-74b6-4bc8-ad68-3197433463aa.png">

Added to $PATH using creating and loading bashrc file as did in step 12

4. Detached GitHub
Commits made in Jenkinsfile and test_app.py file in my VM’s local forked repository were pushed and not accepted by my forked repository on GitHub
 
<img width="626" alt="Screen Shot 2022-09-27 at 11 53 59 PM" src="https://user-images.githubusercontent.com/108698688/192686779-9c57298b-5db8-4b57-ad55-babf9a03f868.png">

Had to edit files directly in GitHub webpage 
 
 <img width="622" alt="Screen Shot 2022-09-27 at 11 54 08 PM" src="https://user-images.githubusercontent.com/108698688/192686807-a52cf6f0-ea3b-44b0-b7a6-4043f0f88543.png">
