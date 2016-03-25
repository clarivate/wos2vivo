
AUTH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
SEARCH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl'

# SOAP message for authenticating.
AUTHENTICATE = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:auth="http://auth.cxf.wokmws.thomsonreuters.com">
  <soapenv:Header/>
   <soapenv:Body>
 	<auth:authenticate/>
 </soapenv:Body>
</soapenv:Envelope>
"""

# SOAP message for closing session.
CLOSE = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:auth="http://auth.cxf.wokmws.thomsonreuters.com">
   <soapenv:Header/>
   <soapenv:Body>
      <auth:closeSession/>
   </soapenv:Body>
</soapenv:Envelope>
"""