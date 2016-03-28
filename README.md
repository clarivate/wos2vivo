##wos2vivo

Mapping publications from the Web of Science™ via [Web Services](http://ipscience-help.thomsonreuters.com/wosWebServicesLite/WebServicesLiteOverviewGroup/Introduction.html) to [VIVO](http://vivoweb.org)

This tool requires access to the Web of Science Web Services. If your organization subscribes to the Web of Science and would like a username and password to use the Web Services, please email `research.networking@thomsonreuters.com`.

The following is supported:
- querying the Web of Science to find publications for a given organization using the [Organization Enhanced](https://images.webofknowledge.com/WOKRS511B5/help/WOS/hp_organizations_enhanced_index.html) name
- specifying a date range for publications to retrieve
- mapping this data to VIVO's RDF for loading into VIVO

###installation

Python 2.7 is required. Install directly from Github:

```
$ pip install git+https://github.com/lawlesst/wos2vivo.git
```

Or clone the repository and install.

```
$ git clone https://github.com/lawlesst/wos2vivo.git
$ cd wos2vivo
$ python setup.py install
```

### usage

The following environment variables are required to configure wos2vivo. 

* DATA_NAMESPACE - the namespace for your VIVO instance
* WOS_USER - the username for accessing the Web of Science Web Services
* WOS_PASSWORD - the password for accessing the Web of Science Web Services

For example:
```
# VIVO data namespace
export DATA_NAMESPACE='http://vivo.school.edu/individual/'
# Web of Science Web Services username and password
export WOS_USER='xxx'
export WOS_PASSWORD='xxx'
```

##### run a harvest 

Only an organization name is required. See a full list of [Organization Enhanced Names](https://images.webofknowledge.com/WOKRS57B4/help/WOS/hs_organizations_enhanced.html) from the Web of Science.

```
$ wos2vivo --help

Usage: wos2vivo [OPTIONS] ORGANIZATION

  Pass in the organization enhanced name from the Web of Science

Options:
  --weeks [1|2|4]          Number of previous weeks to search Web of Science.
  --begin TEXT             Start date for time span search, e.g. 2016-03-15
  --end TEXT               End date for time span search, e.g. 2016-03-17
  --file TEXT              File to save triples to.
  --format [nt|turtle|n3]  RDFLib serialization format
```

##### example
Harvest records for the last two weeks and save to a file called pubs.ttl.

```
$ wos2vivo "Your organization name." --weeks=2 --file=pubs.ttl
```

### data mapping

The publication metadata is mapped from the [Web of Science](http://ipscience-help.thomsonreuters.com/wosWebServicesLite/dataReturnedGroup/dataReturned.html) format to VIVO using the [VIVO-ISF](https://wiki.duraspace.org/display/VIVO/VIVO-ISF+1.6+relationship+diagrams%3A+Authorship) model (VIVO version 1.6 and later).

All author information is mapped to VCARD Names. Local processes will have to be developed to merge the VCARDs to researcher resources in your VIVO system.

###development

#### running the tests
Install test dependencies first with `pip install -r tests/dev_requirements.txt`.

```
$ python -m unittest discover tests/
```

Tests will use [Betamax](http://betamax.readthedocs.org/en/latest/configuring.html) to record
HTTP interactions. This allows us to run the tests without actually hitting the web service and
to keep the sample data stable.

Feedback, bug reports and pull requests welcome.
