#!/homepages/30/d4299101357/htdocs/venv/bin/python3

import os
import sys

# Add the virtual environment's site-packages to the Python path
virtualenv = '/homepages/30/d4299101357/htdocs/venv'
python_version = 'python3.9'
site_packages = os.path.join(virtualenv, 'lib', python_version, 'site-packages')
sys.path.insert(0, site_packages)

# Add the project directory to the Python path
project_dir = '/homepages/30/d4299101357/htdocs'
sys.path.insert(0, project_dir)

# Set up Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'artwork.settings'

from django.core.servers.fastcgi import runfastcgi

runfastcgi(method="threaded", daemonize="false") 