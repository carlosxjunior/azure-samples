# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y wget unzip python3-pip && \
    pip install --upgrade pip && \
    pip install Cython

# Create SAP directory and download SAP NWRFC SDK
RUN mkdir -p /usr/local/sap/ && \
    # TODO: change URL to download the SAP NWRFC SDK
    wget --no-check-certificate -O /usr/local/sap/nwrfc750P_15-70002752_RHEL.zip https://github.com/carlosxjunior/azure-samples/raw/refs/heads/main/Function-Apps/func-container-image/pyrfc/nwrfc750P_15-70002752_RHEL.zip && \
    unzip /usr/local/sap/nwrfc750P_15-70002752_RHEL.zip -d /usr/local/sap/ && \
    rm /usr/local/sap/nwrfc750P_15-70002752_RHEL.zip

# Configure library paths
RUN echo "/usr/local/sap/nwrfcsdk/lib" > /etc/ld.so.conf.d/nwrfcsdk.conf && \
    ldconfig

# Set environment variables
ENV SAPNWRFC_HOME=/usr/local/sap/nwrfcsdk \
    LD_LIBRARY_PATH=/usr/local/sap/nwrfcsdk/lib:$LD_LIBRARY_PATH

# Install PyRFC
RUN pip install pyrfc==3.3.1

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot

# Configure the DNS resolver by writing to /etc/resolv.conf
RUN echo "search one.ofc.loc reddog.microsoft.com\n\
nameserver 10.220.5.128\n\
nameserver 172.18.90.18\n\
nameserver 172.18.44.130" > /etc/resolv.conf