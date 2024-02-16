#!/bin/sh
## set the environment name production/beta/staging
environment=beta
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
cd ../../
docker build --no-cache -t sts-$environment-$branch_name-$date -f Dockerfile.beta .
docker tag sts-$environment-$branch_name-$date 234464546150.dkr.ecr.us-west-2.amazonaws.com/sts:sts-$environment-$branch_name-$date
cd -
echo "Write the Image name to docker-compose-beta.yml & to a separate file for future reference"
sleep 2
sed -i "s|.sts:sts.*|/sts:sts-$environment-$branch_name-$date|g" docker-compose-beta.yml
echo "$date --- $branch --- 234464546150.dkr.ecr.us-west-2.amazonaws.com/sts:sts-$environment-$branch_name-$date">> sts-deployment-version-$environment.txt

docker-compose -f docker-compose-beta.yml down; docker-compose -f docker-compose-beta.yml up -d

echo "done !"
sleep 1