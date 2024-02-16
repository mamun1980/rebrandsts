environment=dev
date=$(date '+%Y-%m-%d-%H-%M')

echo "creating docker image"
docker build -t re-brnad-sts-dev -f Dockerfile.dev .

### Complete Deployment
echo "killing the running docker"
docker ps -a | egrep 're-brnad-sts-dev' | awk '{print $1}'| xargs docker kill
docker ps -a | egrep 're-brnad-sts-dev' | awk '{print $1}'| xargs docker rm

echo "running the Travel Api using docker"
docker run -d --restart=unless-stopped --name re-brnad-sts-dev -p 9000:8000 re-brnad-sts-dev

## Write the deployment history in a file
#echo "$date --- $branch --- re-brnad-sts-$environment-$branch_name-$date">> deployment-version-$environment.txt

echo "We are done !"