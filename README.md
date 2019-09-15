# ComAp API
Allows easy automation of WebSupervisor tasks, such as downloading and analyzing data

The instruction for testing and examples are available on [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

# Documentation
There are two modules available - a simpler synchronos module `comap.api` and asynchronous module `comap.api_async`, that is recommended for use in production.
For better understanding, please look at the examples on the [ComAp-API repository](https://github.com/bruxy70/ComAp-API)

## comap.api 
### Class: comapapi(key,token='')
Use the API ``ComAp-Key`` and ``Token`` to inicialize the object

### Methods
#### authenticate(username,password)
Get the authentication `Token` (for this, the class has to be called with ComAp key without the token)

#### units()
Get list of units with their unitGuid

#### values(unitGuid,valueGuids=None) - 
Get list of values. It is recommended to specify comma separated list of valueGuids to filter the result

#### info(unitGuid)
Get information about the unit

#### comments(unitGuid)
Get comments entered in the WebSupervisor (these can be used for maintenance tasks)

#### history(unitGuid,_from=None,_to=None,valueGuids=None)
Get history of a value. Please specify the valueGuid and `from` and `to` dates in the format `"MM/DD/YYYY"`

#### files(unitGuid)
Get list of files stored on the controller

#### download(unitGuid,fileName,path='')
Download a file from the controller to the current directory (or the directory specified in `path`). You can list the files using the `files` method.

#### command(unitGuid,command,mode=None)
This allows to control the genset. The available commands are `start`,`stop`,`faultReset`,`changeMcb` (toggle mains circuit breaker), `changeGcb` (toggle genset circuit breaker) and `changeMode`. 
For `changeMode` enter the `mode` parameter e.g. to `man` or `auto`

#### get_unit_guid(name)
Find a genset by name. Return is unitGuid

#### get_value_guid(unitGuid,name)
Find a value by name. Return valueGuid

## comap.api_async methods
### Class: comapapi_async(key,token='')
Use the API ``ComAp-Key`` and ``Token`` to inicialize the object

### Methods
Same as comap.api, but each method starting with `async_` - for example `async_units`.