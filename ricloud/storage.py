import shutil

from ricloud import compat


def download_result(url, to_filename=None):
    split_url = compat.urlsplit(url)

    url_type = split_url.scheme
    bucket_name = split_url.netloc
    blob_name = split_url.path

    if url_type == "gs":
        result = download_result_from_gs(
            bucket_name, blob_name, to_filename=to_filename
        )
    elif url_type == "s3":
        result = download_result_from_s3(
            bucket_name, blob_name, to_filename=to_filename
        )
    elif url_type == "local":
        result = download_result_from_local(blob_name, to_filename=to_filename)

    return result


def download_result_from_gs(bucket_name, blob_name, to_filename=None):
    """Download a file from Google Cloud Storage.

    This function assumes that the local environment is configured to access the
    target bucket. This would typically be done through the gcloud command line
    utility. More information can be found here:
    https://cloud.google.com/sdk/gcloud/

    The credentials can also be overriden with Service Account credentials
    directly through the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
    https://cloud.google.com/docs/authentication/getting-started
    """
    try:
        from google.cloud import storage
    except ImportError:
        raise Exception(
            "The google-cloud-storage package is required to download results "
            "from Google Cloud Storage buckets. For details, see: "
            "https://pypi.org/project/google-cloud-storage/"
        )

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    if blob_name[0] == "/":
        blob_name = blob_name[1:]

    blob = bucket.blob(blob_name)

    if to_filename:
        blob.download_to_filename(to_filename)
        return to_filename
    else:
        return blob.download_as_string()


def download_result_from_s3(bucket_name, blob_name, to_filename=None):
    """Download a file from Amazon S3.

    This function assumes the local environment is configured to access the
    target bucket. This would typically be done through AWS credentials and
    configuration files. Some of this is described in the boto3 package
    README here: https://pypi.org/project/boto3/
    """
    try:
        import boto3
    except ImportError:
        raise Exception(
            "The boto3 package is required to download results from Amazon S3 "
            "buckets. For more details, see: https://pypi.org/project/boto3/"
        )

    storage_client = boto3.client("s3")

    if to_filename:
        storage_client.download_file(bucket_name, blob_name, to_filename)
        return to_filename
    else:
        return storage_client.get_object(Bucket=bucket_name, Key=blob_name)


def download_result_from_local(blob_name, to_filename=None):
    if to_filename:
        shutil.copy(blob_name, to_filename)
        return to_filename
    else:
        with open(blob_name, "rb") as f:
            return f.read()
