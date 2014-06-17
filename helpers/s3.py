import boto, os
import boto.s3.connection

class S3():
  def __init__(self, access_key, secret_key, bucket):
    self.conn = boto.connect_s3(
      aws_access_key_id=access_key,
      aws_secret_access_key=secret_key)
    self.bucket = self.conn.get_bucket(bucket)
    if not os.path.exists('cache'):
      os.makedirs('cache')

  def get_url(self, object_key, expires, force_http=False):
    key = self.bucket.get_key(object_key)
    return key.generate_url(expires, query_auth=True, force_http=force_http) if key else None

  def get_file(self, object_key):
    path = 'cache/{}'.format(object_key)
    if not os.path.exists(path):
      key = self.bucket.get_key(object_key)
      key.get_contents_to_filename(path)
    return open(path, 'r')

