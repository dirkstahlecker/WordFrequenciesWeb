# import xmlrpc.client

# with xmlrpc.client.ServerProxy("http://127.0.0.1:5000/test") as proxy:
#     print(proxy != None)
#     print(proxy.system.listMethods())
#     # print(str(proxy.hello('dirk')))
#     # print("3 is even: %s" % str(proxy.test()))
import jsonrpcclient

jsonrpcclient.request('http://127.0.0.1:5000/rpc', 'ping')