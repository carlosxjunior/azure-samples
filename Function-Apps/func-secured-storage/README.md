# Secure an Azure Function App with a virtual network and system managed identity

This tutorial shows how to secure Azure Functions by disabling public access and using a virtual network to connect with other resources. In this demo, the other resources are a secured storage account and a virtual machine, used to deploy code and test our functions.

It also explains how to connect your function app to a storage account with a managed identity instead of a connection string, to avoid accidental leak of sensitive secrets.

## TLDR
✅ Create secured Azure Function App and Storage Account<br>
🔒 Disable public access to resources<br>
🗝️ Use a system managed identity to connect the function app and the storage account<br>
🖥️ Use a VM inside your network to deploy code and test

## Resources deployed in this demo
- 1 Function App
- 1 App Service plan (optional)
- 1 Storage account
- 1 Virtual network
- 6 Network Interfaces
- 5 Private endpoints
- 5 Private DNS zones
- 1 Virtual machine
    - 1 Disk
    - 1 SSH key
    - 1 Network security group
    - 1 Public IP address

## Main references
- [Tutorial: Integrate Azure Functions with an Azure virtual network by using private endpoints](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-vnet)
- [Use managed identity instead of AzureWebJobsStorage to connect a function app to a storage account](https://techcommunity.microsoft.com/blog/appsonazureblog/use-managed-identity-instead-of-azurewebjobsstorage-to-connect-a-function-app-to/3657606)
- [Develop Azure Functions locally using Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python)
- [Install the Azure CLI on Linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)
- [POST JSON Data With Curl](https://www.warp.dev/terminus/post-json-data-with-curl?gad_source=1&gclid=CjwKCAiA74G9BhAEEiwA8kNfpcjAfUb-TqVN_IuZoC-g4XVfid3SMpDr3Vb_vShEEnFQDCTzH1BpOhoCN_wQAvD_BwE)

[GitHub repo with functions code](https://github.com/carlosxjunior/azure-samples/tree/main/Function-Apps/func-secured-storage)

## Let's get to work

### 1) Create a new resource group

Launch the Cloud Shell to use Azure CLI.
<br>![alt text](docs/launch_cli.png)

Run the command `az group create` to create a new RG. Specify the region and the RG name.<br>[Reference](https://learn.microsoft.com/pt-br/cli/azure/group?view=azure-cli-latest)
<br>![alt text](docs/create_rg.png)

The output should look somewhat like this.
<br>![alt text](docs/create_rg_output.png)

### 2) Create the Function App + Storage Account

To create the function app, I followed the step by step in this [guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-vnet#create-a-function-app-in-a-premium-plan).

Inside your new RG, click **Create**.
<br>![alt text](docs/resource_create.png)

Search for function app and select it.
<br>![alt text](docs/func_search.png)

Click **Create** to create a new function app.
<br>![alt text](docs/func_create_screen.png)

Select a hosting option. Here I'm using App Service, but other options will work too. Click **Select**.
<br>![alt text](docs/app_service_select.png)

In the create screen, make sure the right RG is selected. Enter the name of your function app, the runtime, the region (here using the same as the RG), and a name for your app service, as well as the pricing tier (applied if ASP was chosen as the hosting option).

<br>![alt text](docs/func_create_basics.png)

Give the name for a new storage account to be created. You could also create it manually.
<br>![alt text](docs/func_create_storage.png)

Configure the **Networking** options. Make sure to disable public access and enable virtual network configuration.<br>Then, create your networking resources: virtual network, subnets and private endpoints.
<br>![alt text](docs/func_create_net1.png)

<br>![alt text](docs/func_create_net2.png)

After **Networking**, you can skip the other settings and go straight to **Review + create**.
<br>![alt text](docs/func_review_create.png)

### 3) Setup your function app

Go back to your resource group and select your newly created function app.
<br>![alt text](docs/resources_in_rg.png)

Select **Identity**.
<br>![alt text](docs/func_identity.png)

Click **On** to create a system managed identity. Then click on **Azure role assignments**.
<br>![alt text](docs/func_identity_on.png)

Click on **Add role assignment (Preview)**.
<br>![alt text](docs/func_add_role.png)

Assign the role _Storage Blob Data Owner_ to your managed identity in the storage account connected to the function app. Then click on **Save**.
<br>![alt text](docs/add_roles.png)

Repeat the same steps to also add the roles _Storage Account Contributor_ and _Storage Queue Data Owner_ to the managed identity.

Now go back to your storage account, select **Access Control (IAM)**, select **Check access**, seach for your system managed identity for the function app, and check that the correct roles have been assigned.
<br>![alt text](docs/check_roles.png)

Now back to your function app, select **Environment variables**. These variables should pop up.
<br>![alt text](docs/func_envs.png)

We want to delete the default variable `AzureWebJobsStorage`, that holds a connection string for our storage account, and replace it with the `AzureWebJobsStorage__accountName`, with the value as the name of the storage account.
<br>![alt text](docs/func_env_new.png)

Check that the new variable is correctly set. Do not forget to click **Apply**.
<br>![alt text](docs/func_envs_ok.png)

### 4) Create a virtual machine

In order to deploy functions to our function app, we will use a virtual machine inside our virtual network. We cannot deploy from our local machine, for example, as we disabled public access for this app.

Here, search and select Virtual machine.
<br>![alt text](docs/vm_search.png)

Click on **Create**.
<br>![alt text](docs/vm_create.png)

Configure the basic settings for the VM. Give it a name, select a region, an image and the size.<br>For this demo, I'm using a basic VM in the B1s family, with an Ubuntu image.
<br>![alt text](docs/vm_basics.png)

Define your disk settings. I have lowered down the configurations just to make it even cheaper for the demo.
<br>![alt text](docs/vm_disks.png)

Under **Networking**, make sure our virtual network from the function app is selected, otherwise we will not be able to deploy our code.
<br>![alt text](docs/vm_net.png)

Skip the other settings and go to **Review + create**. Click **Create**.
<br>![alt text](docs/vm_review_create.png)

Click the button to download a private key, used to SSH into this VM.
<br>![alt text](docs/vm_pem_key.png)

### 5) Setup virtual machine

Now that our virtual machine is up and running, we need to configure it so we can deploy code to our function app.

We start by getting the VM's public IP address.
<br>![alt text](docs/vm_get_ip.png)

Open a terminal and run the following command to SSH into the VM.
```Powershell
cd Downloads
ssh -i <vm_name>_key.pem azureuser@<vm_public_ip>
```
<br>![alt text](docs/vm_ssh.png)

_Voilá_, we are now connected to our virtual machine.

Now we need to install both the **Azure Functions Core Tools** and the **Azure CLI** in our VM in order to deploy our functions.

For the **Azure Functions Core Tools**, I just followed the steps mentioned [here](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python), which are to run the following commands:
```Bash
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg

sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs 2>/dev/null)-prod $(lsb_release -cs 2>/dev/null) main" > /etc/apt/sources.list.d/dotnetdev.list' # For Ubuntu

sudo apt-get update

sudo apt-get install azure-functions-core-tools-4
```
After that, we can check the installation by running `func -h`. Below is the output of this command.
<br>![alt text](docs/vm_func_help.png)

Installing the **Azure CLI** is even simpler, as explained [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt).

All we have to do is run the command:
```Bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

And then check the installation using `az -h`.
<br>![alt text](docs/vm_az_help.png)

### 6) Deploy code to function app

Now that **Azure Function Core Tools** and the **Azure CLI** are ready, we can finally deploy some functions to our function app.

The code I used for this demo can be found [here](https://github.com/carlosxjunior/azure-samples/tree/main/Function-Apps/func-secured-storage), in my personal repository in GitHub.


Run `az login` to log in to your Azure account. Follow the instructions in the screen.
<br>![alt text](docs/vm_az_login.png)

After opening the link in the browser, using the code and selecting your account, this screen will pop up. You can close your browser and return to the VM.
<br>![alt text](docs/browser_az_login.png)

A similar screen should appear. Select your subscription or press Enter for no changes.
<br>![alt text](docs/vm_az_login_sub.png)

Now, use `git clone` to import the code to our VM.
```Bash
git clone https://github.com/carlosxjunior/azure-samples.git
```
<br>![alt text](docs/vm_git_clone.png)

With the code in our hands, we can deploy it to our function app in Azure. To do so, cd into the directory containing the code and from there, deploy using the **Azure Function Core Tools**, using the command:
```Shell
func azure functionapp publish <function-app-name> --python
```
<br>![alt text](docs/vm_func_deploy.png)

You should see an output similar to this for a successful deployment. _Remote build succeeded!_
<br>![alt text](docs/vm_func_deploy_ok.png)

_Yes!_ Back in Azure Portal, we confirm that our 3 functions have been deployed.
<br>![alt text](docs/func_check_deploy.png)

Let's test them!

### 7) Run your functions

Click in the function name and then click on **Get Function URL**. Copy the URL with the Function key (this setting can be modified in the function code if you don't want to authorize with a key in the request).
<br>![alt text](docs/func_get_url1.png)

Run a POST request from the VM and... it works!
<br>![alt text](docs/vm_run_func1.png)

Now copy the URL into your browser and try to run it from there. It should not work, as we are not allowing public access to this function app.
<br>![alt text](docs/browser_run_func1.png)

We now repeat the process for the other 2 functions.
<br>![alt text](docs/func_get_url2.png)

But first, let's create a container in our storage account to test our functions.
Here the raw container is created.
<br>![alt text](docs/create_container.png)

Function UploadBlob works too!
<br>![alt text](docs/vm_run_func2.png)

Now get the URL for function ReadBlob.
<br>![alt text](docs/vm_get_url3.png)

Awesome, we can read the blob we just created from our other function!
<br>![alt text](docs/vm_run_func3.png)

We cannot access the blob using the Portal, as only access through the virtual network is allowed.
<br>![alt text](docs/storage_check.png)

Once again, we cannot call the function from our machine, as we have successfully secured our function app and storage account.
<br>![alt text](docs/postman_check.png)

## Conclusion
In this tutorial, we have successfully secured an Azure Function App by disabling public access and using a virtual network to connect with other resources. We created a secured storage account and a virtual machine for deploying code and testing our functions. Additionally, we connected the function app to the storage account using a system managed identity, eliminating the need for connection strings and reducing the risk of accidental secret leaks. This setup ensures a more secure and robust environment for your Azure Functions.
