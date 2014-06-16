import boto
import boto.s3.connection

class S3():
  def __init__(self, access_key, secret_key, bucket):
    self.conn = boto.connect_s3(
      aws_access_key_id=access_key,
      aws_secret_access_key=secret_key)
    self.bucket = self.conn.get_bucket(bucket)

  def get_url(object_key, expires):
    key = self.bucket.get_key(object_key)
    return key.generate_url(expires, query_auth=True) if key else None
