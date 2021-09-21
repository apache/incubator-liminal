import io
import os
from git import Repo
import requests
import shutil
import tarfile
import tempfile
from pathlib import Path

import yaml
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from posixpath import join as urljoin # https://stackoverflow.com/a/15279799


class HTTPGetError(RuntimeError):
    def __init__(self, url, code, msg):
        super(RuntimeError, self).__init__(
            'GET %s failed (%d): %s', url, code, msg)


class ChartError(RuntimeError):
    def __init__(self, chart=None):
        if chart:
            super(RuntimeError, self).__init__('Chart not found in repo')
        else:
            super(RuntimeError, self).__init__(
                '%s not found in the repository' % chart)


class VersionError(RuntimeError):
    def __init__(self, version):
        super(RuntimeError, self).__init__(
            'Chart version %s not found' % version)


class SchemeError(RuntimeError):
    def __init__(self, scheme):
        super(RuntimeError, self).__init__(
            'The %s repository not supported' % scheme)


class RepositoryError(RuntimeError):
    def __init__(self, repository):
        super(RuntimeError, self).__init__(
            '%s repository not found' % repository)


def _semver_sorter(x):
    return list(map(int, ''.join(i for i in x['version'] if i in '0123456789.').split('.')))

def _get_from_http(repo_url, file_url, **kwargs):
    """Downloads the Chart's repo index from HTTP(S)"""

    if not bool(urlparse(file_url).netloc):
        file_url = urljoin(repo_url, file_url)

    index = requests.get(file_url, **kwargs)
    if index.status_code >= 400:
        raise HTTPGetError(file_url, index.status_code, index.text)
    return index.content

def _get_from_s3(repo_url, file_url):
    """Download the index / Chart from S3 bucket"""
    import boto3.s3
    from botocore.exceptions import ClientError

    s3_client = boto3.client('s3')

    # NOTE(ljakimczuk): this is done for two
    # reasons. First, it allows to use this
    # function for either getting index.yaml
    # or Chart. Second, at least the Chartmuseum-
    # generated index.yaml may have the relative
    # URLs (guess due to its multi-tenancy), so
    # turning them into absolute is needed.
    if not bool(urlparse(file_url).netloc):
        file_url = urljoin(repo_url, file_url)

    file_url_parsed = urlparse(file_url)

    try:
        file_object = s3_client.get_object(
            Bucket=file_url_parsed.netloc,
            Key=file_url_parsed.path.strip('/'),
        )

        return file_object['Body'].read()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            raise RepositoryError(file_url_parsed.netloc)
        elif e.response['Error']['Code'] == 'NoSuchKey':
            raise ChartError(file_url_parsed.path.strip('/'))
        else:
            raise

def _get_from_repo(repo_scheme, repo_url, file_url, **kwargs):
    """Wrap download from specific repository"""

    if repo_scheme == 's3':
        return _get_from_s3(
            repo_url,
            file_url,
        )
    elif repo_scheme in ('http', 'https'):
        return _get_from_http(
            repo_url,
            file_url,
            **kwargs
        )
    else:
        raise SchemeError(repo_scheme.upper())

def repo_index(repo_url, headers=None):
    """Downloads the Chart's repo index"""
    repo_scheme = urlparse(repo_url).scheme

    return yaml.safe_load(
        _get_from_repo(
            repo_scheme,
            repo_url,
            'index.yaml',
            headers=headers,
        )
    )

def from_repo(repo_url, chart, output_directory=None, version=None, headers=None):
    """Downloads the chart from a repo to a temporary dir, the path of which is
    determined by the platform.
    """
    if output_directory:
        _tmp_dir = Path(output_directory)
    else:
        _tmp_dir = tempfile.mkdtemp(prefix='pyhelm-')
    repo_scheme = urlparse(repo_url).scheme
    index = repo_index(repo_url, headers)

    if chart not in index['entries']:
        raise ChartError()

    versions = index['entries'][chart]

    if version is not None:
        versions = [i for i in versions if i['version'] == version]
    try:
        metadata = sorted(versions, key=_semver_sorter)[-1]
        for url in metadata['urls']:
            data = _get_from_repo(
                repo_scheme,
                repo_url,
                url,
                stream=True,
                headers=headers,
            )
            if isinstance(data, bytes):
                fobj = io.BytesIO(data)
            else:
                fobj = io.StringIO(data)

            tar = tarfile.open(mode="r:*", fileobj=fobj)
            tar.extractall(_tmp_dir)
            return os.path.join(_tmp_dir, chart)
    except IndexError:
        raise VersionError(version)

def git_clone(repo_url, branch='master', path=''):
    """clones repo to a temporary dir, the path of which is determined by the platform"""

    _tmp_dir = tempfile.mkdtemp(prefix='pyhelm-')
    repo = Repo.clone_from(repo_url, _tmp_dir, branch=branch)

    return os.path.join(_tmp_dir, path)

def source_cleanup(target_dir):
    """Clean up source."""
    shutil.rmtree(target_dir)