import datetime
import functools
import os.path
import subprocess
import sys

# Private stable API for detecting the Python implementation.
PYPY = sys.implementation.name == "pypy"

# Private, stable API for detecting the Python version. PYXY means "Python X.Y
# or later". So that third-party apps can use these values, each constant
# should remain as long as the oldest supported DoxHub version supported that
# Python version.
PY38 = sys.version_info >= (3, 8)
PY39 = sys.version_info >= (3, 9)
PY310 = sys.version_info >= (3, 10)
PY311 = sys.version_info >= (3, 11)
PY312 = sys.version_info >= (3, 12)
PY313 = sys.version_info >= (3, 13)


def get_version(version=None):
    """PEP 440-compliant version number

    Build of the two parts of the version number:
    main = X.Y[.Z]
    sub = .devN - for pre-alpha releases
        | {a|b|rc}N - for alpha, beta and rc releases

    Keyword Arguments:
    :param version:             -- Tuple containing the module version.

    :return:
    Return a PEP 440-compliant version number from VERSION.
    """

    version = get_complete_version(version)
    main = get_main_version(version)
    sub = ""

    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = get_git_changeset()
        if git_changeset:
            sub = ".dev%s" % git_changeset
    elif version[3] != "release":
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def get_main_version(version=None):
    """Build main version.

    Return main version (X.Y[.Z]) from VERSION.

    Keyword Arguments:
    :param version:             -- Tuple containing the module version.

    :return:
    Return main version.
    """

    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3

    return ".".join(str(x) for x in version[:parts])


def get_complete_version(version=None):
    """Checking the tuple.

    If version argument is non-empty, check for correctness of
    the tuple provided.

    Keyword Arguments:
    :param version:             -- Tuple containing the module version.

    :return:
    Return a tuple of the DoxHub version.
    """

    if version is None:
        from doxhub import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ('alpha', 'beta', 'rc', 'release')

    return version


@functools.lru_cache
def get_git_changeset():
    """Generating of development version numbers.

    The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.
    This value isn't guaranteed to be unique, but collisions are very unlikely,
    so it's sufficient for generating the development version numbers.

    :return:
    Return a numeric identifier of the latest git changeset.
    """

    if "__file__" not in globals():
        return None

    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_log = subprocess.run(
        "git log --pretty=format:%ct --quiet -1 HEAD",
        capture_output=True,
        shell=True,
        cwd=repo_dir,
        text=True
    )

    timestamp = git_log.stdout
    tz = datetime.timezone.utc

    try:
        timestamp = datetime.datetime.fromtimestamp(int(timestamp), tz=tz)
    except ValueError:
        return None

    return timestamp.strftime("%Y%m%d%H%M%S")
