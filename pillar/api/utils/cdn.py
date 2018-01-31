import datetime
from hashlib import md5
import base64

from flask import current_app


def hash_file_path(file_path, expiry_timestamp=None):
    if not file_path.startswith('/'):
        file_path = '/' + file_path
    service_domain = current_app.config['CDN_SERVICE_DOMAIN']
    domain_subfolder = current_app.config['CDN_CONTENT_SUBFOLDER']
    asset_url = current_app.config['CDN_SERVICE_DOMAIN_PROTOCOL'] + \
                '://' + \
                service_domain + \
                domain_subfolder + \
                file_path

    if current_app.config['CDN_USE_URL_SIGNING']:

        url_signing_key = current_app.config['CDN_URL_SIGNING_KEY']
        to_hash = domain_subfolder + file_path + url_signing_key

        if not expiry_timestamp:
            expiry_timestamp = datetime.datetime.now() + datetime.timedelta(hours=24)
            expiry_timestamp = expiry_timestamp.strftime('%s')

        to_hash = expiry_timestamp + to_hash
        if isinstance(to_hash, str):
            to_hash = to_hash.encode()

        expiry_timestamp = "," + str(expiry_timestamp)

        hashed_file_path = base64.b64encode(md5(to_hash).digest())[:-1].decode()
        hashed_file_path = hashed_file_path.replace('+', '-').replace('/', '_')

        asset_url = asset_url + \
                    '?secure=' + \
                    hashed_file_path + \
                    expiry_timestamp

    return asset_url
