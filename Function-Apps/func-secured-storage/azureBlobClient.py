import os
import logging

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

class AzureBlobClient:
    def __init__(self, connection_string: str=None, account_name: str=None):
        """
        Initializes the AzureBlobClient with a BlobServiceClient.
        :param connection_string: Connection string for the storage account.
        :param account_name: Name of the storage account to create the account URL for managed identity authentication.
        """
        self.blob_service_client = self.create_blob_service_client(connection_string, account_name)

    def create_blob_service_client(self, connection_string: str=None, account_name: str=None) -> BlobServiceClient:
        """
        Returns a BlobServiceClient based on the provided connection method.
        :param connection_string: Connection string for the storage account.
        :param account_name: Name of the storage account to create the account URL for managed identity authentication.
        :return: BlobServiceClient instance.
        """
        if connection_string:
            try:
                logging.info("[Azure Blob Integration]: Using connection string for authentication.")
                return BlobServiceClient.from_connection_string(connection_string)
            except Exception as e:
                logging.error(f"[Azure Blob Integration]: Error creating BlobServiceClient: {e}.")
                raise
        elif account_name:
            try:
                logging.info("[Azure Blob Integration]: Using managed identity for authentication.")
                credential = DefaultAzureCredential()
                account_url = f"https://{account_name}.blob.core.windows.net"
                return BlobServiceClient(account_url=account_url, credential=credential)
            except Exception as e:
                logging.error(f"[Azure Blob Integration]: Error creating BlobServiceClient: {e}.")
                raise
        else:
            logging.error("[Azure Blob Integration]: Either a connection string or an account URL must be provided.")
            raise ValueError("Either a connection string or an account URL must be provided.")

    def list_blobs(self, container_name: str, path: str="") -> list[str]:
        """
        Lists all blobs in a specific path within a container.
        :param container_name: Name of the container in the data lake.
        :param path: Path to list blobs from (use an empty string to list all blobs in the container).
        :return: List of blob names.
        """
        try:
            # Get the container client
            container_client = self.blob_service_client.get_container_client(container_name)

            # List blobs in the specified path
            blob_list = container_client.list_blobs(name_starts_with=path)
            blobs = [blob.name for blob in blob_list]

            logging.info(f"[Azure Blob Integration]: Found these blobs in path '{path}': {blobs}.")
            return blobs

        except Exception as e:
            logging.error(f"[Azure Blob Integration]: Error in function list_blobs: {e}.")
            raise

    def read_blob(self, container_name: str, blob_name: str) -> str:
        """
        Reads the content of a blob from Azure Blob Storage.
        :param container_name: The name of the container containing the blob.
        :param blob_name: The name of the blob to read.
        :return: The content of the blob as a string.
        """
        try:
            # Get a client for the specified container
            container_client = self.blob_service_client.get_container_client(container_name)
            # Get a client for the specified blob
            blob_client = container_client.get_blob_client(blob_name)

            # Download the blob's content as a string
            blob_data = blob_client.download_blob().readall()
            blob_content = blob_data.decode('utf-8')  # Decode bytes to string

            logging.info(f"[Azure Blob Integration]: Successfully read blob: {blob_name}.")
            return blob_content
        except Exception as e:
            logging.error(f"[Azure Blob Integration]: Error trying to read blob {blob_name} from container {container_name}: {e}.")
            raise

    def upload_blob_from_data(self, container_name: str, blob_name: str, data: bytes, overwrite: bool=True) -> None:
        """
        Uploads data (bytes) to Azure Blob Storage as a blob.
        :param container_name: Name of the container in the data lake.
        :param blob_name: Name of the blob in Azure Blob Storage.
        :param data: Data to upload (bytes).
        :param overwrite: Whether to overwrite the blob if it already exists (default is True).
        :return: None
        """
        try:
            # Get the container client
            container_client = self.blob_service_client.get_container_client(container_name)

            # Upload the data
            container_client.upload_blob(name=blob_name, data=data, overwrite=overwrite)
            logging.info(f"[Azure Blob Integration]: Data uploaded successfully to blob '{blob_name}' in container '{container_name}'.")

        except Exception as e:
            logging.error(f"[Azure Blob Integration]: Error uploading data to blob '{blob_name}' in container {container_name}: {e}.")
            raise

    def upload_blob_from_file(self, container_name: str, filepath: str, filename: str, blob_name: str = None, overwrite: bool = True) -> None:
        """
        Uploads a local file to Azure Blob Storage.
        :param container_name: Name of the container in the data lake.
        :param filepath: Local directory path where the file is located.
        :param filename: Name of the local file to upload.
        :param blob_name: Name of the blob in Azure Blob Storage (defaults to the local filename if not provided).
        :param overwrite: Whether to overwrite the blob if it already exists (default is True).
        :return: None
        """
        try:
            # Construct the full local file path
            full_file_path = os.path.join(filepath, filename)

            # If blob_name is not provided, use the local filename as the blob name
            if not blob_name:
                blob_name = filename

            # Get the container client
            container_client = self.blob_service_client.get_container_client(container_name)

            # Upload the file
            with open(file=full_file_path, mode="rb") as data:
                container_client.upload_blob(name=blob_name, data=data, overwrite=overwrite)

            logging.info(f"[Azure Blob Integration]: File '{filename}' uploaded successfully to blob '{blob_name}' in container '{container_name}'.")

        except FileNotFoundError:
            logging.error(f"[Azure Blob Integration]: The file '{filename}' was not found at path '{filepath}'.")
            raise
        except Exception as e:
            logging.error(f"[Azure Blob Integration]: Error uploading file '{filename}' to blob '{blob_name}': {e}.")
            raise

    def upload_blob(self, container_name: str, blob_name: str, data: bytes=None, filepath: str=None, filename: str=None, overwrite: bool=True) -> None:
        """
        Uploads data or a file to Azure Blob Storage.
        :param container_name: Name of the container in the data lake.
        :param blob_name: Name of the blob in Azure Blob Storage.
        :param data: Data to upload (bytes). If provided, this will be used for the upload.
        :param filepath: Local directory path where the file is located (required if filename is provided).
        :param filename: Name of the local file to upload (required if filepath is provided).
        :param overwrite: Whether to overwrite the blob if it already exists (default is True).
        :return: None
        """
        if data is not None:
            # Upload data directly
            self.upload_blob_from_data(container_name, blob_name, data, overwrite)
        elif filepath is not None and filename is not None:
            # Upload from a file
            self.upload_blob_from_file(container_name, filepath, filename, blob_name, overwrite)
        else:
            raise ValueError("Either 'data' or both 'filepath' and 'filename' must be provided.")