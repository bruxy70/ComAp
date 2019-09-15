"""
comap.api module
"""
import logging, json
import os
from datetime import datetime, date, time, timedelta
import requests
import timestring
from .constants import URL

API_KEY = 'Comap-Key'
API_TOKEN = 'Token'

_LOGGER = logging.getLogger(__name__)

class ErrorGettingData(Exception):
    """Raised when we cannot get data from API"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class comapapi():
    """Constructor"""
    def __init__(self,key,token=''):
        """Setup of the czpubtran library"""
        self._api_key = key
        self._api_token = token
    
    def _call_api(self,api,unitGuid=None,payload={}):
        """Call ComAp API. Return None if not succesfull"""
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return None
        if api not in URL:
            _LOGGER.error( f'Unknown API {api}!')
            return None
        headers = {API_TOKEN:self._api_token,API_KEY: self._api_key}
        try:
            _url= URL[api] if unitGuid is None else URL[api].format(unitGuid)
            response = requests.get(_url,headers=headers,params=payload)
            _LOGGER.debug( f'Calling API url {response.url}')
            if response.status_code!= 200:
                _LOGGER.error( f'API {api} returned code: {response.status_code} ({response.reason}) ')    
                return None
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return None
        return response.json()

    def units(self):
        """Get list of all units - returns a list of xxx with two values: name,unitGuid"""
        response_json = self._call_api('units')
        return [] if response_json is None else response_json['units']

    def values(self,unitGuid,valueGuids=None):
        """Get Genset values"""
        if valueGuids==None:
            response_json = self._call_api('values',unitGuid)
        else:
            response_json = self._call_api('values',unitGuid,{'valueGuids':valueGuids})
        values = [] if response_json is None else response_json['values']
        for value in values:
            value["timeStamp"]=timestring.Date(value["timeStamp"]).date
        return values


    def info(self,unitGuid):
        """Get Genset info"""
        response_json = self._call_api('info',unitGuid)
        return [] if response_json is None else response_json

    def comments(self,unitGuid):
        """Get Genset comments"""
        response_json = self._call_api('comments',unitGuid)
        comments = [] if response_json is None else response_json['comments']
        for comment in comments:
            comment["date"]=timestring.Date(comment["date"]).date
        return comments

    def history(self,unitGuid,_from=None,_to=None,valueGuids=None):
        """Get Genset history"""
        payload={}
        if _from is not None: payload['from'] = _from
        if _to is not None: payload['to'] = _to
        if valueGuids is not None: payload['valueGuids'] = valueGuids 
        response_json = self._call_api('history',unitGuid,payload=payload)
        values = [] if response_json is None else response_json['values']
        for value in values:
            for entry in value["history"]:
                entry["validTo"]=timestring.Date(entry["validTo"]).date
        return values

    def files(self,unitGuid):
        """Get Genset files"""
        response_json = self._call_api('files',unitGuid)
        files=[] if response_json is None else response_json['files']
        for file in files:
            file["generated"]=timestring.Date(file["generated"]).date
        return files

    def authenticate(self,username,password):
        if self._api_key is None:
            _LOGGER.error( f'API Comap-Key not available!')
            return None
        api="authenticate"
        headers = {API_KEY: self._api_key,'Content-Type':'application/json'}
        body={'username':username,'password':password}
        try:
            _url= URL[api]
            response = requests.post(_url,headers=headers,json=body)
            _LOGGER.debug( f'Calling API url {response.url}')
            if response.status_code!= 200:
                _LOGGER.error( f'API {api} returned code: {response.status_code} ({response.reason}) ')    
                return None
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return None
        response_json=response.json()
        self._api_token = '' if response_json is None else response_json['applicationToken']
        return self._api_token

    def download(self,unitGuid,fileName,path=''):
        "download file"
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return False
        headers = {API_TOKEN:self._api_token,API_KEY: self._api_key}
        try:
            api='download'
            _url= URL[api].format(unitGuid,fileName)
            _LOGGER.debug( f'url {_url}')
            response = requests.get(_url,headers=headers)
            if response.status_code!= 200:
                _LOGGER.error( f'API {api} returned code: {response.status_code} ({response.reason}) ')    
                return False
            _LOGGER.debug( f'Calling API url {response.url}')
            with open(os.path.join(path,fileName), 'wb') as f:
                f.write(response.content)
            f.close()
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return False
        return True

    def command(self,unitGuid,command,mode=None):
        "send command"
        if self._api_key is None or self._api_token is None:
            _LOGGER.error( f'API Token and Comap-Key not available!')
            return False
        headers = {API_TOKEN:self._api_token,API_KEY: self._api_key,'Content-Type':'application/json'}
        body={'command':command}
        if command=='mode': body['mode']=mode
        try:
            api='command'
            _url= URL[api].format(unitGuid)
            response = requests.post(_url,headers=headers,json=body)
            if response.status_code!= 200:
                _LOGGER.error( f'API {api} returned code: {response.status_code} ({response.reason}) ')    
                return False
            _LOGGER.debug( f'Calling API url {response.url}')
        except Exception as e:
            _LOGGER.error( f'API {api} error {e}')
            return False
        return True

    def get_unit_guid(self,name):
        """Find GUID for unit name"""
        unit = next((unit for unit in self.units() if unit['name'].find(name)>=0),None)
        return None if unit==None else unit['unitGuid']

    def get_value_guid(self,unitGuid,name):
        """Find guid of a value"""
        value = next((value for value in self.values(unitGuid) if value['name'].find(name)>=0),None)
        return None if value==None else value['valueGuid']