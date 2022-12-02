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

# Release

[PyPI](https://pypi.org), Python Package Index, is a repository of software for the Python programming language.

## Install or Upgrade package

We use [build](https://pypi.org/project/build/) to build package, and [twine](https://pypi.org/project/twine/) to
upload package to PyPi. You could first install and upgrade them by:

```bash
python3 -m pip install --upgrade pip build twine
```

It is highly recommended [releasing package to TestPyPi](#release-to-testpypi) first, to check whether the
package is correct, and then [release to PyPi](#release-to-pypi).

## Release to TestPyPi

TestPyPi is a test environment of PyPi, you could release to it to test whether the package is work or not.

1. Create an account in [TestPyPi](https://test.pypi.org/account/register/).
2. Clean unrelated files in `dist` directory, and build package `python3 setup.py clean`.
3. Build package `python3 -m build`, and you will see two new files in `dist` directory, with extension
   `.tar.gz` and `.whl`.
4. Upload to TestPyPi `python3 -m twine upload --repository testpypi dist/*`.
5. Check the package in [TestPyPi](https://test.pypi.org/project/airtolphin/) and install it
   by `python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps airtolphin` to
   test whether it is work or not.

## Release to PyPi

PyPi is the official repository of Python packages, it is highly recommended [releasing package to TestPyPi](#release-to-testpypi)
first to test whether the package is correct.

### Automatically

After you check the package in TestPyPi is correct, you can directly tag the commit and push it to GitHub, then
GitHub Actions will automatically release to PyPi based on the tag event. You can see more detail in [pypi-workflow.yml](.github/workflows/pypi.yaml).

```shell
tag_val=0.0.1
git tag -a "${tag_val}" -m "Release v${tag_val}"
git push --tags
```

### Manually

1. Create an account in [PyPI](https://pypi.org/account/register/).
2. Clean unrelated files in `dist` directory, and build package `python3 setup.py clean`.
3. Build package `python3 -m build`, and you will see two new files in `dist` directory, with extension
   `.tar.gz` and `.whl`.
4. Upload to TestPyPi `python3 -m twine upload dist/*`.
5. Check the package in [PyPi](https://pypi.org/project/airtolphin/) and install it
   by `python3 -m pip install airtolphin` to install it.

## Ref

There is an official way to package project from [PyPA](https://packaging.python.org/en/latest/tutorials/packaging-projects)
