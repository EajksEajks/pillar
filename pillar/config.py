import os.path
from collections import defaultdict

RFC1123_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

SCHEME = 'http'
STORAGE_DIR = '/data/storage/pillar'
SHARED_DIR = '/data/storage/shared'
PORT = 5000
HOST = '0.0.0.0'
DEBUG = False

# Authentication settings
BLENDER_ID_ENDPOINT = 'http://blender_id:8000/'

CDN_USE_URL_SIGNING = True
CDN_SERVICE_DOMAIN_PROTOCOL = 'https'
CDN_SERVICE_DOMAIN = 'test-blendercloud.r.worldssl.net'
CDN_CONTENT_SUBFOLDER = ''
CDN_URL_SIGNING_KEY = '-SECRET-'

CDN_STORAGE_USER = '-SECRET'
CDN_STORAGE_ADDRESS = 'push-11.cdnsun.com'
CDN_SYNC_LOGS = '/data/storage/logs'
CDN_RSA_KEY = '/data/config/cdnsun_id_rsa'
CDN_KNOWN_HOSTS = '/data/config/known_hosts'

UPLOADS_LOCAL_STORAGE_THUMBNAILS = {
    's': {'size': (90, 90), 'crop': True},
    'b': {'size': (160, 160), 'crop': True},
    't': {'size': (160, 160), 'crop': False},
    'm': {'size': (320, 320), 'crop': False},
    'l': {'size': (1024, 1024), 'crop': False},
    'h': {'size': (2048, 2048), 'crop': False}
}

BIN_FFPROBE = '/usr/bin/ffprobe'
BIN_FFMPEG = '/usr/bin/ffmpeg'
BIN_SSH = '/usr/bin/ssh'
BIN_RSYNC = '/usr/bin/rsync'

GCLOUD_APP_CREDENTIALS = os.path.join(os.path.dirname(__file__), 'google_app.json')
GCLOUD_PROJECT = 'blender-cloud'

ADMIN_USER_GROUP = '5596e975ea893b269af85c0e'
SUBSCRIBER_USER_GROUP = '5596e975ea893b269af85c0f'
BUGSNAG_API_KEY = ''

ALGOLIA_USER = '-SECRET-'
ALGOLIA_API_KEY = '-SECRET-'
ALGOLIA_INDEX_USERS = 'dev_Users'
ALGOLIA_INDEX_NODES = 'dev_Nodes'

ZENCODER_API_KEY = '-SECRET-'
ZENCODER_NOTIFICATIONS_SECRET = '-SECRET-'
ZENCODER_NOTIFICATIONS_URL = 'http://zencoderfetcher/'

ENCODING_BACKEND = 'zencoder'  # local, flamenco

# Validity period of links, per file storage backend. Expressed in seconds.
# Shouldn't be more than a year, as this isn't supported by HTTP/1.1.
FILE_LINK_VALIDITY = defaultdict(
    lambda: 3600 * 24 * 30,  # default of 1 month.
    gcs=3600 * 23,  # 23 hours for Google Cloud Storage.
)

