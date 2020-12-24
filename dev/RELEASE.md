<!--
 Licensed to the Apache Software Foundation (ASF) under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  The ASF licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing,
 software distributed under the License is distributed on an
 "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 KIND, either express or implied.  See the License for the
 specific language governing permissions and limitations
 under the License.
-->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Apache Liminal source releases](#apache-liminal-source-releases)
  - [Apache Liminal Package](#apache-liminal-package)
- [Prerequisites for the release manager preparing the release](#prerequisites-for-the-release-manager-preparing-the-release)
  - [version IDs](#version-ids)
  - [Testing the release locally](#testing-the-release-locally)
  - [Upload Public keys to id.apache.org](#upload-public-keys-to-idapacheorg)
  - [Configure PyPI uploads](#configure-pypi-uploads)
  - [Hardware used to prepare and verify the packages](#hardware-used-to-prepare-and-verify-the-packages)
- [Apache Liminal packages](#apache-liminal-packages)
  - [Prepare the Apache Liminal Package RC](#prepare-the-apache-liminal-package-rc)
    - [Build RC artifacts (both source packages and convenience packages)](#build-rc-artifacts-both-source-packages-and-convenience-packages)
    - [Prepare PyPI convenience "snapshot" packages](#prepare-pypi-convenience-snapshot-packages)
  - [Vote and verify the Apache Liminal release candidate](#vote-and-verify-the-apache-liminal-release-candidate)
    - [Prepare Vote email on the Apache Liminal release candidate](#prepare-vote-email-on-the-apache-liminal-release-candidate)
    - [Verify the release candidate by PMCs (legal)](#verify-the-release-candidate-by-pmcs-legal)
      - [PMC responsibilities](#pmc-responsibilities)
      - [SVN check](#svn-check)
      - [Verify the licences](#verify-the-licences)
      - [Verify the signatures](#verify-the-signatures)
      - [Verify the SHA512 sum](#verify-the-sha512-sum)
    - [Verify if the release candidate "works" by Contributors](#verify-if-the-release-candidate-works-by-contributors)
  - [Publish the final Apache Liminal release](#publish-the-final-apache-liminal-release)
    - [Summarize the voting for the Apache Liminal release](#summarize-the-voting-for-the-apache-liminal-release)
    - [Publish release to SVN](#publish-release-to-svn)
    - [Prepare PyPI "release" packages](#prepare-pypi-release-packages)
    - [Update CHANGELOG.md](#update-changelogmd)
    - [Notify developers of release](#notify-developers-of-release)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Apache Liminal source releases

## Apache Liminal Package

This package contains sources that allow the user building fully-functional Apache Liminal package.
They contain sources for "apache-liminal" python package that installs "liminal" Python package and includes
all the assets required to release the webserver UI coming with Apache Liminal

The Source releases are the only "official" Apache Software Foundation releases, and they are distributed
via [Official Apache Download sources](https://downloads.apache.org/)

Following source releases Apache Liminal release manager also distributes convenience packages:

* PyPI packages released via https://pypi.org/project/apache-liminal/
* Docker Images released via https://hub.docker.com/repository/docker/apache/liminal (coming soon...)

Those convenience packages are not "official releases" of Apache Liminal, but the users who
cannot or do not want to build the packages themselves can use them as a convenient way of installing
Apache Liminal, however they are not considered as "official source releases". You can read more
details about it in the [ASF Release Policy](http://www.apache.org/legal/release-policy.html).

This document describes the process of releasing both - official source packages and convenience
packages for Apache Liminal packages.

# Prerequisites for the release manager preparing the release

The person acting as release manager has to fulfill certain pre-requisites. More details and FAQs are
available in the [ASF Release Policy](http://www.apache.org/legal/release-policy.html) but here some important
pre-requisites are listed below. Note that release manager does not have to be a PMC - it is enough
to be committer to assume the release manager role, but there are final steps in the process (uploading
final releases to SVN) that can only be done by PMC member. If needed, the release manager
can ask PMC to perform that final step of release.

## version IDs

Should follow https://www.python.org/dev/peps/pep-0440/

## Testing the release locally

- Build a local version of liminal:
```bash
# Set Version
export LIMINAL_BUILD_VERSION=0.0.1rc1
python setup.py sdist bdist_wheel
```

- Start a test project with a liminal .yml file in it

- Clear folder $LIMINAL_HOME

- Install liminal in the test project

```bash
pip install <path to lminal .whl created by setup.py>
liminal build
liminal deploy --clean
liminal start
```

Note:
When you run liminal deploy, a liminal installs itself inside airflow container.
You can control which version of liminal gets installed inside docker using LIMINAL_VERSION environment variable.

This can be any string which results in a legal call to:
```bash
pip install ${LIMINAL_VERSION}
```

This includes 
- A standard pip version like apache-liminal==0.0.1dev1 avail from pypi
- A URL for git e.g. git+https://github.com/apache/incubator-liminal.git
- A string indicating where to get the package from like --index <url> apache-liminal==xyz
- A local path to a .whl which is available inside the docker (e.g. which you placed
in the scripts/ folder)

This is useful if you are making changes in liminal locally and want to test them.

If you don't specify this variable, liminal attempts to discover how to install itself
by running a pip freeze and looking at the result. 
This covers pip repositories, files and installtion from URL.

The fallback in case no string is found, is simply 'apache-liminal' assuming your .pypirc contains an 
index which has this package.

## Upload Public keys to id.apache.org

Make sure your public key is on id.apache.org and in KEYS. You will need to sign the release artifacts
with your pgp key. After you have created a key, make sure you:

- Add your GPG pub key to https://dist.apache.org/repos/dist/release/liminal/KEYS , follow the instructions at the top of that file. Upload your GPG public key to https://pgp.mit.edu
- Add your key fingerprint to https://id.apache.org/ (login with your apache credentials, paste your fingerprint into the pgp fingerprint field and hit save).

```shell script
# Create PGP Key
gpg --gen-key

# Checkout ASF dist repo
svn checkout https://dist.apache.org/repos/dist/release/incubator/liminal
cd liminal


# Add your GPG pub key to KEYS file. Replace "Aviem Zur" with your name
(gpg --list-sigs "Aviem Zur" && gpg --armor --export "Aviem Zur" ) >> KEYS


# Commit the changes
svn commit -m "Add PGP keys of Liminal developers"
```

See this for more detail on creating keys and what is required for signing releases.

http://www.apache.org/dev/release-signing.html#basic-facts

## Configure PyPI uploads

In order to not reveal your password in plain text, it's best if you create and configure API Upload tokens.
You can add and copy the tokens here:

* [Test PyPI](https://test.pypi.org/manage/account/token/)
* [Prod PyPI](https://pypi.org/manage/account/token/)


Create a `~/.pypirc` file:

```ini
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
username=__token__
password=<API Upload Token>

[pypitest]
repository=https://test.pypi.org/legacy/
username=__token__
password=<API Upload Token>
```

Set proper permissions for the pypirc file:

```shell script
$ chmod 600 ~/.pypirc
```

- Install [twine](https://pypi.org/project/twine/) if you do not have it already (it can be done
  in a separate virtual environment).

```shell script
pip install twine
```

(more details [here](https://peterdowns.com/posts/first-time-with-pypi.html).)

- Set proper permissions for the pypirc file:
`$ chmod 600 ~/.pypirc`

## Hardware used to prepare and verify the packages

The best way to prepare and verify the releases is to prepare them on a hardware owned and controlled
by the committer acting as release manager. While strictly speaking, releases must only be verified
on hardware owned and controlled by the committer, for practical reasons it's best if the packages are
prepared using such hardware. More information can be found in this
[FAQ](http://www.apache.org/legal/release-policy.html#owned-controlled-hardware)

# Apache Liminal packages

## Prepare the Apache Liminal Package RC

### Build RC artifacts (both source packages and convenience packages)

The Release Candidate artifacts we vote upon should be the exact ones we vote against, without any modification than renaming – i.e. the contents of the files must be the same between voted release canidate and final release. Because of this the version in the built artifacts that will become the official Apache releases must not include the rcN suffix.

- Set environment variables

```bash
# Set Version
export LIMINAL_BUILD_VERSION=0.0.1rc1

# Example after cloning
git clone https://github.com/apache/incubating-liminal.git 
cd incubating-liminal
```
  
- Tag your release

```bash
git tag -a ${LIMINAL_BUILD_VERSION} -m "some message"

```

- Clean the checkout: the sdist step below will

```bash
git clean -fxd
```

- Tarball the repo

```bash
git archive --format=tar.gz ${LIMINAL_BUILD_VERSION} --prefix=apache-liminal-${LIMINAL_BUILD_VERSION}/ -o apache-liminal-${LIMINAL_BUILD_VERSION}-source.tar.gz
```


- Generate sdist

    NOTE: Make sure your checkout is clean at this stage - any untracked or changed files will otherwise be included
     in the file produced.

```bash
python setup.py sdist bdist_wheel
```

- Generate SHA512/ASC (If you have not generated a key yet, generate it by following instructions on http://www.apache.org/dev/openpgp.html#key-gen-generate-key)

```bash
dev/sign.sh apache-liminal-${LIMINAL_BUILD_VERSION}-source.tar.gz
dev/sign.sh dist/apache-liminal-${LIMINAL_BUILD_VERSION}.tar.gz
dev/sign.sh dist/apache_liminal-${LIMINAL_BUILD_VERSION}-py3-none-any.whl
```

- Push Tags

```bashs
git push origin ${LIMINAL_BUILD_VERSION}
```

- Push the artifacts to ASF dev dist repo
```
# First clone the repo
svn checkout https://dist.apache.org/repos/dist/dev/liminal liminal-dev

# Create new folder for the release
cd liminal-dev
svn mkdir ${LIMINAL_BUILD_VERSION}

# Move the artifacts to svn folder & commit
mv apache{-,_}liminal-${LIMINAL_BUILD_VERSION}* ${LIMINAL_BUILD_VERSION}/
cd ${LIMINAL_BUILD_VERSION}
svn add *
svn commit -m "Add artifacts for Liminal ${LIMINAL_BUILD_VERSION}"
```

### Prepare PyPI convenience "snapshot" packages

At this point we have the artefact that we vote on, but as a convenience to developers we also want to
publish "snapshots" of the RC builds to pypi for installing via pip. To do this we need to

- Verify the artifacts that would be uploaded:

```bash
twine check dist/*
```

- Upload the package to PyPi's test environment:

```bash
twine upload -r pypitest dist/*
```

- Verify that the test package looks good by downloading it and installing it into a virtual environment. The package download link is available at:
https://test.pypi.org/project/apache-liminal/#files

- Upload the package to PyPi's production environment:
`twine upload -r pypi dist/*`

- Again, confirm that the package is available here:
https://pypi.python.org/pypi/apache-liminal


It is important to stress that this snapshot should not be named "release", and it
is not supposed to be used by and advertised to the end-users who do not read the devlist.

## Vote and verify the Apache Liminal release candidate

### Prepare Vote email on the Apache Liminal release candidate

- Use the dev/liminal-jira script to generate a list of Liminal JIRAs that were closed in the release.

- Send out a vote to the dev@liminal.apache.org mailing list:

Subject:
```
[VOTE] Liminal 1.10.2rc3
```

Body:

```
Hey all,

I have cut Liminal 1.10.2 RC3. This email is calling a vote on the release,
which will last for 72 hours. Consider this my (binding) +1.

Liminal 1.10.2 RC3 is available at:
https://dist.apache.org/repos/dist/dev/liminal/1.10.2rc3/

*apache-liminal-1.10.2rc3-source.tar.gz* is a source release that comes
with INSTALL instructions.
*apache-liminal-1.10.2rc3-bin.tar.gz* is the binary Python "sdist" release.

Public keys are available at:
https://dist.apache.org/repos/dist/release/liminal/KEYS

Only votes from PMC members are binding, but the release manager should encourage members of the community
to test the release and vote with "(non-binding)".

The test procedure for PMCs and Contributors who would like to test this RC are described in
https://github.com/apache/liminal/blob/master/dev/README.md#vote-and-verify-the-apache-liminal-release-candidate

Please note that the version number excludes the `rcX` string, so it's now
simply 1.10.2. This will allow us to rename the artifact without modifying
the artifact checksums when we actually release.


Changes since 1.10.2rc2:
*Bugs*:
[LIMINAL-3732] ...
...


*Improvements*:
[LIMINAL-3302] ...
...


*New features*:
[LIMINAL-2874] ...
...


*Doc-only Change*:
[LIMINAL-XXX] Fix Minor issues in Documentation
...

Cheers,
<your name>
```

### Verify the release candidate by PMCs (legal)

#### PMC responsibilities

The PMCs should verify the releases in order to make sure the release is following the
[Apache Legal Release Policy](http://www.apache.org/legal/release-policy.html).

At least 3 (+1) votes should be recorded in accordance to
[Votes on Package Releases](https://www.apache.org/foundation/voting.html#ReleaseVotes)

The legal checks include:

* checking if the packages are present in the right dist folder on svn
* verifying if all the sources have correct licences
* verifying if release manager signed the releases with the right key
* verifying if all the checksums are valid for the release

#### SVN check

The files should be present in the sub-folder of
[Liminal dist](https://dist.apache.org/repos/dist/dev/incubator/liminal/)

The following files should be present (9 files):

* .tar.gz + .asc + .sha512
* -.whl + .asc + .sha512

As a PMC you should be able to clone the SVN repository:

```shell script
    svn co https://dist.apache.org/repos/dist/dev/incubator/liminal
```

Or update it if you already checked it out:

```shell script
svn update .
```

#### Verify the licences

This can be done with the Apache RAT tool.

* Download the latest jar from https://creadur.apache.org/rat/download_rat.cgi (unpack the sources,
  the jar is inside)
* Unpack the .tar.gz to a folder
* Enter the folder and run the check (point to the place where you extracted the .jar)

```shell script
java -jar ../../apache-rat-0.13/apache-rat-0.13.jar -E .rat-excludes -d .
```

#### Verify the signatures

Make sure you have the key of person signed imported in your GPG. You can find the valid keys in
[KEYS](https://dist.apache.org/repos/dist/release/liminal/KEYS).

You can import the whole KEYS file:

```shell script
gpg --import KEYS
```

You can also import the keys individually from a keyserver. The below one uses Kaxil's key and
retrieves it from the default GPG keyserver
[OpenPGP.org](https://keys.openpgp.org):

```shell script
gpg --receive-keys 12717556040EEF2EEAF1B9C275FCCD0A25FA0E4B
```

You should choose to import the key when asked.

Note that by being default, the OpenPGP server tends to be overloaded often and might respond with
errors or timeouts. Many of the release managers also uploaded their keys to the
[GNUPG.net](https://keys.gnupg.net) keyserver, and you can retrieve it from there.

```shell script
gpg --keyserver keys.gnupg.net --receive-keys 12717556040EEF2EEAF1B9C275FCCD0A25FA0E4B
```

Once you have the keys, the signatures can be verified by running this:

```shell script
for i in *.asc
do
   echo "Checking $i"; gpg --verify `basename $i .sha512 `
done
```

This should produce results similar to the below. The "Good signature from ..." is indication
that the signatures are correct. Do not worry about the "not certified with a trusted signature"
warning. Most of the certificates used by release managers are self signed, that's why you get this
warning. By importing the server in the previous step and importing it via ID from
[KEYS](https://dist.apache.org/repos/dist/release/liminal/KEYS) page, you know that
this is a valid Key already.

```
Checking apache-liminal-1.10.12rc4-bin.tar.gz.asc
gpg: assuming signed data in 'apache-liminal-1.10.12rc4-bin.tar.gz'
gpg: Signature made sob, 22 sie 2020, 20:28:28 CEST
gpg:                using RSA key 12717556040EEF2EEAF1B9C275FCCD0A25FA0E4B
gpg: Good signature from "Kaxil Naik <kaxilnaik@gmail.com>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 1271 7556 040E EF2E EAF1  B9C2 75FC CD0A 25FA 0E4B
Checking apache_liminal-1.10.12rc4-py2.py3-none-any.whl.asc
gpg: assuming signed data in 'apache_liminal-1.10.12rc4-py2.py3-none-any.whl'
gpg: Signature made sob, 22 sie 2020, 20:28:31 CEST
gpg:                using RSA key 12717556040EEF2EEAF1B9C275FCCD0A25FA0E4B
gpg: Good signature from "Kaxil Naik <kaxilnaik@gmail.com>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 1271 7556 040E EF2E EAF1  B9C2 75FC CD0A 25FA 0E4B
Checking apache-liminal-1.10.12rc4-source.tar.gz.asc
gpg: assuming signed data in 'apache-liminal-1.10.12rc4-source.tar.gz'
gpg: Signature made sob, 22 sie 2020, 20:28:25 CEST
gpg:                using RSA key 12717556040EEF2EEAF1B9C275FCCD0A25FA0E4B
gpg: Good signature from "Kaxil Naik <kaxilnaik@gmail.com>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 1271 7556 040E EF2E EAF1  B9C2 75FC CD0A 25FA 0E4B
```

#### Verify the SHA512 sum

Run this:

```shell script
for i in *.sha512
do
    echo "Checking $i"; gpg --print-md SHA512 `basename $i .sha512 ` | diff - $i
done
```

You should get output similar to:

```
Checking apache_liminal-1.10.12rc4-py3-none-any.whl.sha512
Checking apache-liminal-1.10.12rc4.tar.gz.sha512
```

### Verify if the release candidate "works" by Contributors

This can be done (and we encourage to) by any of the Contributors. In fact, it's best if the
actual users of Apache Liminal test it in their own staging/test installations. Each release candidate
is available on PyPI apart from SVN packages, so everyone should be able to install
the release candidate version of Liminal via simply (<VERSION> is 1.10.12 for example, and <X> is
release candidate number 1,2,3,....).

```shell script
pip install apache-liminal==<LIMINAL_BUID_VERSION>rc<X>
```

## Publish the final Apache Liminal release

### Summarize the voting for the Apache Liminal release

Once the vote has been passed, you will need to send a result vote to dev@liminal.apache.org:

Subject:
```
[RESULT][VOTE] Liminal 1.10.2rc3
```

Message:

```
Hello,

Apache Liminal 1.10.2 (based on RC3) has been accepted.

3 “+1” binding votes received:
....

3 "+1" non-binding votes received:

...

Vote thread:
...

I'll continue with the release process, and the release announcement will follow shortly.

Cheers,
<your name>
```


### Publish release to SVN

You need to migrate the RC artifacts that passed to this repository:
https://dist.apache.org/repos/dist/release/liminal/
(The migration should include renaming the files so that they no longer have the RC number in their filenames.)

The best way of doing this is to svn cp  between the two repos (this avoids having to upload the binaries again, and gives a clearer history in the svn commit logs):

```shell script
# First clone the repo
export RC=1.10.4rc5
export VERSION=${RC/rc?/}
svn checkout https://dist.apache.org/repos/dist/release/liminal liminal-release

# Create new folder for the release
cd liminal-release
svn mkdir ${VERSION}
cd ${VERSION}

# Move the artifacts to svn folder & commit
for f in ../../liminal-dev/$RC/*; do svn cp $f ${$(basename $f)/rc?/}; done
svn commit -m "Release Liminal ${VERSION} from ${RC}"

# Remove old release
# http://www.apache.org/legal/release-policy.html#when-to-archive
cd ..
export PREVIOUS_VERSION=1.10.1
svn rm ${PREVIOUS_VERSION}
svn commit -m "Remove old release: ${PREVIOUS_VERSION}"
```

Verify that the packages appear in [liminal](https://dist.apache.org/repos/dist/release/liminal/)

### Prepare PyPI "release" packages

At this point we release an official package:

- Build the package:

    ```shell script
    python setup.py sdist bdist_wheel`
    ```

- Verify the artifacts that would be uploaded:

    ```shell script
    twine check dist/*`
    ```

- Upload the package to PyPi's test environment:

    ```shell script
    twine upload -r pypitest dist/*
    ```

- Verify that the test package looks good by downloading it and installing it into a virtual environment.
    The package download link is available at: https://test.pypi.org/project/apache-liminal/#files

- Upload the package to PyPi's production environment:

    ```shell script
    twine upload -r pypi dist/*
    ```

- Again, confirm that the package is available here: https://pypi.python.org/pypi/apache-liminal

### Update CHANGELOG.md

- Get a diff between the last version and the current version:

    ```shell script
    $ git log 1.8.0..1.9.0 --pretty=oneline
    ```
- Update CHANGELOG.md with the details, and commit it.

### Notify developers of release

- Notify users@liminal.apache.org (cc'ing dev@liminal.apache.org and announce@apache.org) that
the artifacts have been published:

Subject:
```shell script
cat <<EOF
Liminal ${VERSION} is released
EOF
```

Body:
```shell script
cat <<EOF
Dear Liminal community,

I'm happy to announce that Liminal ${VERSION} was just released.

The source release, as well as the binary "sdist" release, are available
here:

https://dist.apache.org/repos/dist/release/liminal/${VERSION}/

We also made this version available on PyPi for convenience (`pip install apache-liminal`):

https://pypi.python.org/pypi/apache-liminal

The documentation is available on:
https://liminal.apache.org/
https://liminal.apache.org/1.10.2/
https://liminal.readthedocs.io/en/1.10.2/
https://liminal.readthedocs.io/en/stable/

Find the CHANGELOG here for more details:

https://liminal.apache.org/changelog.html#liminal-1-10-2-2019-01-19

Cheers,
<your name>
EOF
```
