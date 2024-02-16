#!/bin/sh
## set the environment name production/beta/staging
environment=$environment
date=$(date '+%Y-%m-%d-%H-%M')
### Pull branch
echo "Please enter branch name to pull:"
read branch
echo you have entered branch : $branch
sleep 2
cd ../../
git stash; git branch -f origin/$branch; git checkout $branch; git pull;

echo 'Modify the branch name'
cd -
echo $branch > branch_name_file
sed -i 's/\//-/g' branch_name_file
sed -i 's/\./-/g' branch_name_file
branch_name=$(<branch_name_file)
echo "The branch name is replace to : $branch_name"
sleep 1

echo "prepare the docker image"
docker build --no-cache -t sts-$environment-$branch_name-$date ../../.
docker tag sts-$environment-$branch_name-$date 234464546150.dkr.ecr.us-west-2.amazonaws.com/sts:sts-$environment-$branch_name-$date

echo "login to aws"
sleep 1
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 234464546150.dkr.ecr.us-west-2.amazonaws.com

echo "push image to ecr"
docker push 234464546150.dkr.ecr.us-west-2.amazonaws.com/sts:sts-$environment-$branch_name-$date

echo "Write the Image name to docker-compose.yml & to a separate file for future reference"
sleep 2
# sed -i "s|.sts:sts.*|/sts:sts-$branch_name-$date|g" Dockerfile
sed -i "s|.sts:sts.*|/sts:sts-$environment-$branch_name-$date|g" docker-compose.yml
echo "$date --- $branch --- 234464546150.dkr.ecr.us-west-2.amazonaws.com/sts:sts-$environment-$branch_name-$date">> sts-deployment-version-$environment.txt

# Before deploy in the elastic beanstalk, please update the environd name in the eb deploy command.
echo "deploying to EBS environment"
eb deploy environment-name -l "$environment-$branch_name-$date" -m "$environment-$branch_name-$date"

echo "done !"
sleep 1