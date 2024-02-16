environment=staging
date=$(date '+%Y-%m-%d-%H-%M')

### Pull branch
echo "Please enter branch name to pull:"
read branch
echo you have entered branch : $branch
sleep 1
echo "Updatting from git"
git stash; git branch -f origin/$branch; git checkout $branch; git pull;

echo "creating docker image"
docker build -t re-brnad-sts-staging -f Dockerfile.staging .

### Complete Deployment
echo "killing the running docker"
docker ps -a | egrep 're-brnad-sts-staging' | awk '{print $1}'| xargs docker kill
docker ps -a | egrep 're-brnad-sts-staging' | awk '{print $1}'| xargs docker rm

echo "running the Travel Api using docker"
docker run -d --restart=unless-stopped --name re-brnad-sts-staging -p 9001:8000 re-brnad-sts-staging

## Write the deployment history in a file
#echo "$date --- $branch --- re-brnad-sts-$environment-$branch_name-$date">> deployment-version-$environment.txt

echo "We are done !"