# Overview

This file describes how to create an environment for `AWS Elastic Beanstalk` and the deployment process within the created environment for `production`. It also provides instructions for `staging` and `beta` deployments.

## Environment Settings

 - Go to the `AWS Elastic Beanstalk` console & create an **Environment** using the `Docker` Platform with the following **configuration**.

   - Capacity:
        - **Environment type**: Load Balancer
        - Instances: Min 2 Max 4 (or as per the requirements.)
        - **Fleet composition**: Combine purchase options and instances
        - Set your spot price & Instance type.
        - **Scaling** RequestCount or Latency or Time-based scaling, which is suitable for the environment.
   - Load Balancer:
        - Application
        - Store Logs if required
   - Rolling updates and deployments:
     - Rolling
   - Security:
     - EC2 key pair: deploy-srv
   - VPC:
     - VRS - VPC
     - Visibility: Internal
   - Notification:
     - Email: XXXXXXX@w3engineers.com
   - Managed updates
      - Instance replacement: disabled
      - Managed updates: enabled

### AWS EB Environment Details for Production
  - **Applications**: internal-searchtewak
  - **Environment**: sts

**Note:** `Elastic Beanstalk ` will create the required Security groups, which is enough for this project to run.

# Production Deployment

   - ssh -i pem.pem ubuntu@54.70.204.95
   - Install AWS `eb cli` & `AWS cli`
   - Need AWS IAM permission to deploy in the `Elastic Beanstalk` environment.

   - Clone the project
     - git clone https://code.lefttravel.com/vrs/re-brand-sts.git
   - Set the environment in `/home/ubuntu/re-brand-sts/deployment/eb` from `.env.sample`
   - **Note**: Always sync with .env.sample for latest config.

   - Initialize:
     - cd `~/home/ubuntu/re-brand-sts/deployment/eb`
     - Now initialize the project by the command `eb init`.
   - Update `.ebignore` file and add all the file that you want the `EB` to ignore.
   - Deployment:
      - Create `docker-compose.yml` file from `docker-compose-sample.yml` .
      - copy the file `deployment-sample.sh` for your deployment environment & change the required values.
      - `cp deployment-sample.sh production-deployment.sh`
      - run the file  `production-deployment.sh`
      ```/bin/bash
      bash production-deployment.sh
      ```
      - It will ask for the `project branch` and will deploy automatically to the `EB` environment.
      - **Note**: the EB environment name has to be updated in `production-deployment.sh` file.

## Staging/Beta Deployment
Clone the repo   
```commandline
$ git clone https://code.lefttravel.com/vrs/re-brand-sts.git  
$ cd  re-brand-sts   
```
  - Copy `docker-compose-(environment)-sample.yml` file to `docker-compose-(environment).yml`   
  - Set the environment in `re-brand-sts/deployment/eb` from `.env.sample`   
  - **Note**: Always sync with .env.sample for latest config.   
  - Run the respected bash file for Staging/Beta for local deployments.    
