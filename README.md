# CZDS

[![PyPI](https://img.shields.io/pypi/v/czds.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/czds.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/czds)][pypi status]
[![License](https://img.shields.io/pypi/l/czds)][license]

[![Read the documentation at https://czds.readthedocs.io/](https://img.shields.io/readthedocs/czds/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/MSAdministrator/czds/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/MSAdministrator/czds/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/czds/
[read the docs]: https://czds.readthedocs.io/
[tests]: https://github.com/MSAdministrator/czds/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/MSAdministrator/czds
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## What is CZDS?

Each Top Level Domain (TLD) is maintained by a registry operator, who also manages a publicly available list of Second Level Domains (SLDs) and the details needed to resolve those domain names to Internet Protocol (IP) addresses.

The registry operator’s zone data contains the mapping of domain names, associated name server names, and IP addresses for those name servers. These details are updated by the registry operator for its respective TLDs whenever information changes or a domain name is added or removed.

Each registry operator keeps its zone data in a text file called the Zone File which is updated once every 24 hours.

## Features

- Retrieve Centralized Zone Transfer Files from root DNS servers hosted by ICAAN and other agencies
- Download one or all of the zone files to your local system/disk
- You can now retrieve zone files using multi-threading

## Requirements

- You need a CZDS account with ICAAN. You can sign-up [here](https://czds.icann.org)
- Internet access

## Installation

You can install _CZDS_ via [pip] from [PyPI]:

```console
$ pip install czds
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## Developmemt

If you are using `pyenv` to manage your enviroments you can set a config option in poetry to use the set pyenv version of python by running this:

```bash
poetry config virtualenvs.prefer-active-python true
poetry install
```
## License

Distributed under the terms of the [MIT license][license],
_CZDS_ is free and open source software.

## Security

Security concerns are a top priority for us, please review our [Security Policy](SECURITY.md).

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@MSAdministrator]'s [Hypermodern Python Cookiecutter] template.

[@MSAdministrator]: https://github.com/MSAdministrator
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/MSAdministrator/czds/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/MSAdministrator/czds/blob/main/LICENSE
[contributor guide]: https://github.com/MSAdministrator/czds/blob/main/CONTRIBUTING.md
[command-line reference]: https://czds.readthedocs.io/en/latest/usage.html
