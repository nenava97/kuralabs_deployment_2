# Deployment 2 Kura Labs Nicole Navarrete 09.27.22

## Purpose: Set up a CI/CD pipeline using a GitHub repository with a url-shortener app code which is then built out and tested with AWS CLI on a Jenkins EC2 and finally deployed from Elastic Beanstalk CLI

## Create  AWS EC2 and set up dependencies needed for Jenkins

1. Create an EC2 on AWS with the following configurations:
ubuntu Amazon Machine Image
t2.micro free tier eligible instance type
create and download a new key pair on VM if don’t already have one (RSA key pair type and .pem private key file format ex key.pem),
security groups (ssh, 22, 0.0.0.0/0) (HTTPS, 80, 0.0.0.0/0) (HTTPS, 8080, 0.0.0.0/0),
 
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
![ScreenShot](screenshot.jpg)


## Install Jenkins on an EC2

7. Followed Jenkins documentation on how to install jenkins in Linux system (https://www.jenkins.io/doc/book/installing/linux/#debianubuntu )
```
$ curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \ /usr/share/keyrings/jenkins-keyring.asc > /dev/null
$ echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \ https://pkg.jenkins.io/debian-stable binary/ | sudo tee \ /etc/apt/sources.list.d/jenkins.list > /dev/null
$sudo apt-get update
$sudo apt-get install jenkins
```

## Activate the Jenkins user on the EC2

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

## Create a Jenkins user in your AWS account

10. In IAM dashboard click on Users under Access Management and add a new user with the following configurations:
Access key - Programmatic Access
Set permissions, click on attach existing policies directly and check off Administrator Access
Create user and make sure to copy and save Access Key ID and Secret Access Key made

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

## Install EB CLI in the Jenkins EC2 user

12. Followed AWS Elastic Beanstalk documentation on how to manually install the EB CLI (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install-advanced.html)
```
$ pip install awsebcli --upgrade --user 
$ eb --version
```
![ScreenShot](screenshot.jpg)

Take note of the LOCAL_PATH where scripts are installed in so can add to $PATH
```
$ nano .bashrc
```
![ScreenShot](screenshot.jpg)

Load profile script with the export command in current session
```
$ source ./.bashrc
```

## Connect GitHub to Jenkins Server

13. Fork repository https://github.com/kura-labs-org/kuralabs_deployment_2 
14. Create personal access token in GitHub
Click on account settings 
go to Developer Settings all the way at the bottom of left-side box
click Personal access tokens and press generate new tokens
select scopes repo and admin:repo_hook
Copy token to use in next step

## Update Jenkinsfile and test_app.py in GitHub forked Repo

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

## Create a multibranch build

17. Configure Jenkins
Open browser and enter http:\\<<EC2PublicIPv4address>>:8080
Create Jenkins profile
In Jenkins Dashboard 
Add New Item
Enter item name (ex url-shortener) and select Multibranch Pipeline
Enter display name (ex Build Flask) and Description (ex CI/CD pipeline deployment 2)
Add Branch Source as GitHub
Add Jenkins 
Enter GitHub username and paste access token as password
Enter forked repository url and validate 
Ensure Build Configuration says Jenkinsfile
Apply and Save
Select Scan repository if build doesn’t automatically start creating

## Deploy application from Elastic Beanstalk CLI

18. Configure project directory
```
$sudo su - jenkins -s /bin/bash
$cd /var/workspace/url-shortner/
$eb init
```
Follow configuration options in screenshots below
![ScreenShot](screenshot.jpg)
![ScreenShot](screenshot.jpg)


```
$eb create
```
![ScreenShot](screenshot.jpg)
![ScreenShot](screenshot.jpg)




19. Test environment
Click on url AWS created for your environment and make sure the web page opens without error
![ScreenShot](screenshot.jpg)
![ScreenShot](screenshot.jpg)



## Errors

1. Permissions
In step 11 got errors that jenkins user was not a sudoer, and therefore couldn’t install or run 
![ScreenShot](screenshot.jpg)

Had to exit sudo user and edit sudoer file as in step 6
![ScreenShot](screenshot.jpg)



2. Dependencies
![ScreenShot](screenshot.jpg)
![ScreenShot](screenshot.jpg)

When made first build of application got errors that the python test couldn’t run 
Had to install python as did in step 4
![ScreenShot](screenshot.jpg)




3. PATH error
Path for eb couldn’t be found when tried to run deployment after updating Jenkinsfile and test_app.py in step 15
![ScreenShot](screenshot.jpg)


Added to $PATH using creating and loading bashrc file as did in step 12

4. Detached GitHub
Commits made in Jenkinsfile and test_app.py file in my VM’s local forked repository were pushed and not accepted by my forked repository on GitHub 
![ScreenShot](screenshot.jpg)
![ScreenShot](screenshot.jpg)


Had to edit files directly in GitHub webpage 
![ScreenShot](screenshot.jpg)
