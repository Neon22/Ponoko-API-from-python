### Using Python to communicate with the Ponoko API
### public domain license

### Author: M. Schafer
### date: Jan 2012


### Ensure you use your own api keys here.
### This code will not work without proper keys.
app_key = ("app_key", " abcdefgh ")
user_access_key = ("user_access_key", " stuvwxyz ")


# Use live system or Sandbox
#live_or_test = "www"
live_or_test = "sandbox"

# Used for all API access
baseURL = "http://"+ live_or_test +".ponoko.com/services/api/v2"
material_catalogTAG = "/material_catalog/" # added onto nodesTAG
nodesTAG = "/nodes" # added onto baseURL

#Imports
from urllib2 import Request, urlopen
from urllib import urlencode, quote
import json
from datetime import datetime
from copy import deepcopy


### Dummy Structure to show update.
### Replace with your own datastructure from database.
Node_materials = {'Ponoko - United States': [u'2010/06/28 20:23:16',
                {'6bb50fb04a' :
                     {u'material_type': u'printed',
                      u'updated_at': u'2011/06/27 20:23:16 +0000',
                      u'key': u'6bb500cdb04a',
                      u'name': u'Durable plastic'}},
                 {'6b62cdbed4a' :
                     {u'material_type': u'printed',
                      u'updated_at': u'2011/06/27 20:23:16 +0000',
                      u'key': u'6bb9552cdb04a',
                      u'name': u'Rainbow Ceramic'}}
                ]
            }

###
def basic_request(request, verbose=False):
    """ request is in form of a urllib2.Request()
        Return (False, error) OR
        (True, response, url, info)
        """
    error = False
    result = []
    try:
        response = urlopen(request,timeout=100)
    except IOError, e:
        if hasattr(e,'reason'):
            error = ("FAILED to reach server", e.reason)
        elif hasattr(e, 'code'):
            error = ("FAIL - Server could not fulfill request", e.code)
    except Exception as inst:
        error = ("unspecified error occurred", inst.args)
    else: # all good
        result = (response.read(), response.geturl(), response.info())
        if verbose:
            print "Requested:\n  %s" % request
            print "Response:\n  %s" % result
        return (True, result)
    # Failed - return error codes
    if verbose:
        print "Error", error
    return (False, error)


def get_manufacturing_nodes(URL, keydata, verbose=True):
    """ Get the nodes from dedicated url.
        Uses basic request
    """
    URL_full = "%s%s?%s" % (URL, nodesTAG, keydata)
    if verbose:
        print "Getting Node catalog\n  %s" % (URL_full)
    req = Request(URL_full)
    success, result = basic_request(req)
    if not success:
        # fail!!
        if verbose: print "Error:", result
        return (False, result)
    else: # Success
        nodes = json.loads(result[0])['nodes']
        if verbose:
            print "Response:\n  %s" % (nodes)
            # for each node
            for i in range(len(nodes)):
                print "Node name", nodes[i][u'name']
                print "  Last updated:", nodes[i][u'materials_updated_at']
                print "  node_key", nodes[i][u'key']
        return (True, nodes)


def update_node_materials(node, URL, keydata, verbose=True):
    """ for a manufacturing node:
        - retrieve the catalog in json format
        - convert it to python dictionary and list structures
    """
    location = node[u'name']
    date =     node[u'materials_updated_at']
    key =      node[u'key']
    date = date[:-6] # strip off seconds
    recorded_materials = Node_materials[location]
    ourdate = datetime.strptime(recorded_materials[0], "%Y/%m/%d %H:%M:%S")
    newdate = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
    if verbose: print "Checking: %s vs. %s" % (ourdate, newdate)
    if ourdate <= newdate:
        # need to update some or all materials
        catalog = recorded_materials[1]
        catalogURL = "%s%s%s" % (URL, nodesTAG, material_catalogTAG)
        request = "%s%s?%s" %(catalogURL, key, keydata)
        if verbose: print "Requesting Catalog updates for %s\n  %s" % (location, request)
        req = Request(request)
        result = basic_request(req)
        if not result[0]:
            # fail
            print result[1]
        else: # Success
            materials = json.loads(result[1][0])
            show_materials(materials, location)
            # update the local store
            #!!!
    else: # no need to update
        print "No change to materials for %s" % (location)


def show_materials(materials, location):
    """ show what's in the materials catalog """
    key_superset = []
    key_commonset = []
    #
    key = materials['key']
    count = materials['count']
    catalog = materials['materials']
    if count != len(catalog):
        # something not right
        print "Expecting count to be same as length of catalog"
        print "Failing..."
    else: # good
        print "Location: %s" % (location)
        print "  %s materials found" % (count)
        for c in catalog:
            keys = c.keys()
            keys.sort()
            # collect superset of all keys
            for k in keys:
                if k not in key_superset:
                    key_superset.append(k)
            #
            print " ", c['name']
            if c['name'] == 'Cork':
                print c['key'], c['weight'], c['thickness']
##            if u'weight' in keys:
##                print c['name']
##                print " ", c
##                #print " ",c['type']
##                #print " ",c['kind']
##                #print " ",c['updated_at']
##                #print " ", keys
##            if u'type' not in keys:
##                print c['name']
##                print " ", c
        # Find common set of keys
        key_commonset = deepcopy(key_superset)
        for c in catalog:
            keys = c.keys()
            for k in key_commonset:
                if k not in keys:
                    key_commonset.remove(k)
        #
        print "Superset of all keys found is:", key_superset
        print "Common set of keys is:", key_commonset




## main
if __name__ == "__main__":#
    keydata = urlencode((app_key, user_access_key))
    success, nodes = get_manufacturing_nodes(baseURL, keydata)
    if success:
        print success, nodes
        for i in range(len(nodes)):
            update_node_materials(nodes[i], baseURL, keydata)

