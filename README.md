##wos2vivo

Mapping publications from the Web of Science™ via [Web Services Lite](http://ipscience-help.thomsonreuters.com/wosWebServicesLite/WebServicesLiteOverviewGroup/Introduction.html) to [VIVO](http://vivoweb.org)


###usage

This toolkit requires Python 2.7.

* Clone the git repository:

```
$ git clone https://github.com/lawlesst/wos2vivo.git
```

* Install the Python dependencies
```
$ cd wos2vivo
$ pip install -r requirements
```

* Set environment variables
```
$ cp .env.sample .env
# adjust values to match your VIVO data namespace and Web of Science username and password
$ source .env
```


