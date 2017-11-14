## wos2vivo

Mapping publications from the Web of Science™ via [Web Services Lite](https://clarivate.com/products/data-integration/) to [VIVO](http://vivoweb.org)

This tool requires access to the Web of Science Web Services. If your organization subscribes to the Web of Science and would like a username and password to use the Web Services, please email `research.networking@clarivate.com`.

### installation

Python 2.7 is required. Install directly from Github:

```
$ pip install git+https://github.com/Clarivate-SAR/wos2vivo.git
```

Or clone the repository and install.

```
$ git clone https://github.com/Clarivate-SAR/wos2vivo.git
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

Only an organization name is required. See more information on [Organization Enhanced Names](https://images.webofknowledge.com/images/help/WOS/hp_organizations_enhanced_index.html) from the Web of Science.

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

The publication metadata is mapped from the [Web of Science](http://ipscience-help.thomsonreuters.com/wosWebServicesLite/dataReturnedGroup/dataReturned.html) format to VIVO using the [VIVO-ISF](https://wiki.duraspace.org/x/P76dB) model (VIVO version 1.6 and later).

Example output:
```
d:pub-WOS-000411369700071 a bibo:AcademicArticle ;
    rdfs:label "Coherent J/psi photoproduction in ultra-peripheral PbPb collisions at root s(NN)=2.76 TeV with the CMS experiment" ;
    obo:ARG_2000028 d:vcard-individual-pub-WOS-000411369700071 ;
    bibo:doi "10.1016/j.physletb.2017.07.001" ;
    bibo:end "511" ;
    bibo:start "489" ;
    bibo:volume "772" ;
    vivo:dateTimeValue d:date-WOS-000411369700071 ;
    vivo:hasPublicationVenue d:venue-0370-2693 ;
    vivo:identifier "WOS:000411369700071" .

d:authorship-1-WOS-000411369700071 a vivo:Authorship ;
    vivo:rank 1 ;
    vivo:relates d:pub-WOS-000411369700071,
        d:vcard-individual-1-WOS-000411369700071 .

d:vcard-individual-1-WOS-000411369700071 a vcard:Individual ;
    vcard:hasName d:vcard-name-1-WOS-000411369700071 .

d:vcard-name-1-WOS-000411369700071 a vcard:Name ;
    rdfs:label "Khachatryan, V." ;
    vcard:familyName "Khachatryan" ;
    vcard:givenName "V." .

d:vcard-individual-pub-WOS-000411369700071 a vcard:Individual ;
    vcard:hasURL d:vcard-url-pub-WOS-000411369700071 .

d:vcard-url-pub-WOS-000411369700071 a vcard:URL ;
    rdfs:label "Web of Science™" ;
    vcard:url "http://ws.isiknowledge.com/cps/openurl/service?url_ver=Z39.88-2004&rft_id=info:ut/WOS:WOS:000411369700071" .

d:venue-0370-2693 a bibo:Journal ;
    rdfs:label "PHYSICS LETTERS B" ;
    bibo:issn "0370-2693" .

d:date-WOS-000411369700071 a vivo:DateTimeValue ;
    rdfs:label "SEP, 2017" ;
    vivo:dateTime "2017-9"^^xsd:dayMonth ;
    vivo:dateTimePrecision vivo:yearMonthPrecision .

```

All author information is mapped to vCard Names. Local processes will have to be developed to merge the vCards to foaf:Person researcher resources in your VIVO system.

### development

#### running the tests
Install test dependencies first with `pip install -r tests/dev_requirements.txt`.

```
$ python -m unittest discover
```

Tests will use [Betamax](http://betamax.readthedocs.org/en/latest/configuring.html) to record HTTP interactions. This allows us to run the tests without actually hitting the web service and to keep the sample data stable.

Feedback, bug reports and pull requests welcome.
