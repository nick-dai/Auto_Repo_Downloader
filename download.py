#!/usr/bin/python3

import os
from urllib.parse import urlparse
import re

URL_TYPES = {
    'git': { # GitHub repos
        'extension': '.git',
        'url_pattern': r'^(http).*(\.git)$',
        'download': 'git clone $url;',
        'update': 'cd $filename; git pull;'
    },
    'gz': { # .tar.gz files
        'extension': '.tar.gz',
        'url_pattern': r'(\.tar\.gz)$',
        'download': 'mkdir ./$filename; wget $url; tar xvzf $filename.tar.gz -C ./$filename; rm -rf $filename.tar.gz;',
        'update': 'rm $filename -rf; #download'
    },
    'bz2': { # .tar.bz2 files
        'extension': '.tar.bz2',
        'url_pattern': r'(\.tar\.bz2)$',
        'download': 'mkdir ./$filename; wget $url; tar xvfj $filename.tar.bz2 -C ./$filename; rm -rf $filename.tar.bz2;',
        'update': 'rm $filename -rf; #download'
    },
    'svn': { # SVN repos
        'extension': None,
        'url_pattern': r'svn',
        'download': 'svn co $url $filename;',
        'update': 'cd $filename; svn up;',
        'filename': r'/(\w+)/(?:trunk|branches)'
    },
    'sf': { # SourceForge repos
        'extension': None,
        'url_pattern': r'sf\.net',
        'download': 'git clone $url $filename;',
        'update': 'cd $filename; git pull;',
        'filename': r'/(\w+)/(?:code)'
    },
    'zip': { # .zip files
        'extension': '.zip',
        'url_pattern': r'(\.zip)$',
        'download': 'mkdir $filename; unzip $filename.zip -d ./$filename;',
        'update': 'rm $filename -rf; #download'
    },
}

def get_url_by_string(line):
    """
    Extract git URL from a string.
    """
    return line.split('#')[0].strip()

def classify_url(url):
    for u_type in URL_TYPES.keys():
        if re.search(URL_TYPES[u_type]['url_pattern'], url):
            return u_type
    return None

def download_or_update(u_type, url):
    """Download the files or update them by git.

    Some preserved words can be used in 'download' or 'update' command:
        $filename: the filename extracted by get_filename_by_url().
        $url: the fetched URL from source.txt.
        #download: reuse scripts in 'download'.
    """
    filename = get_filename_by_url(u_type, url)
    if os.path.exists(os.path.join('.', filename)):
        cmd = URL_TYPES[u_type]['update']
    else:
        cmd = URL_TYPES[u_type]['download']
    cmd = cmd.replace('$url', url).replace('$filename', filename).replace('#download', URL_TYPES[u_type]['download'])
    return os.system(cmd)

def get_filename_by_url(u_type, url):
    """Extract the filename without any extension.

    It reads settings from URL_TYPES to identify what the filename is.
    It first checks the 'filename' setting in URL_TYPES,
    and extracts the first occurrance by regex's group to be the filename.
    If the filename still cannot be set,
    then read 'extension' setting to cut up the file's extension.
    """
    filename = None
    if 'filename' in URL_TYPES[u_type]:
        # First occurrance of the target will be the filename.
        filename = re.search(URL_TYPES[u_type]['filename'], url).group(1)
    if not filename:
        filename = os.path.basename(urlparse(url).path)
        filename = filename.replace(URL_TYPES[u_type]['extension'], '') if 'extension' in URL_TYPES[u_type] else os.path.splitext(filename)[0]
    return filename

if __name__ == '__main__':
    with open('./source.txt', 'r') as file:
        for ln in file.readlines():
            url = get_url_by_string(ln)
            url_type = classify_url(url)
            if url_type:
                print('- Downloading {}...'.format(url))
                download_or_update(url_type, url)
            else:
                print('- No valid URL. Skipped.')
        print('- Done!')
