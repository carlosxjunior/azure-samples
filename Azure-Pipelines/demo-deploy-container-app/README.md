Describe what has been done in order to build the image to the Container Registry and deploy it to the Function App.


Install docker engine in the self-hosted agent VM: https://docs.docker.com/engine/install/ubuntu/
Create group docker and add the user 'azureuser'. First check what user is running the pipelines. https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
Restart the agent. I did it by updating the agent in the portal