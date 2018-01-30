import xmlrpc.client

with xmlrpc.client.ServerProxy("http://127.0.0.1:5000/") as proxy:
    print(str(proxy.hello('dirk')))