from WindowsNotification import notify
import requests
import ssl
import json
import threading
import time
import os
import websocket
import SimpleHTTPServer
import SocketServer
import webbrowser


class GroupMe:

    request_URL = "oauth.groupme.com/oauth/authorize?client_id=DRHcjc2QwMkHNtoB0dP6o3skAzIhhVo2j9oja3d26c0l83gr"
    access_token = ""
    access_token_dir = "access_token"
    clientId = ""
    userid = ""
    PORT = 8000
    server = ""  # Object used for capturing the access token
    requestid = 1
    cacert = "cacert.pem"

    def __init__(self):
        print "New Instance of GroupMe"

    # Method for connecting to GroupMe
    def handshake(self):
        # Exact handshake string
        data = """
    [
      {
        "channel":"/meta/handshake",
        "version":"1.0",
        "supportedConnectionTypes":["websocket"],
        "id":"""+str(self.requestid)+"""
      }
    ]
    """
        print "Handshake..."
        print "Sending (POST): %s" % data
        r = requests.post('https://push.groupme.com/faye', data=data, json=None, verify=self.cacert,
                          headers={'content-type': 'application/json'})
        # Increase id
        self.increment_request_id()
        print "Received:"
        print r.text
        p = json.loads(r.text)
        if p[0]['successful'] is True:
            self.clientId = p[0]["clientId"]
            print "Handshake complete\n"

    # Method to get API access token from GroupMe
    def auth(self):
        # If access_token file doesn't exist or is empty
        if not os.path.isfile(self.access_token_dir) or os.stat(self.access_token_dir).st_size == 0:
            self.startserver()
            print "access_token file not found"
            webbrowser.open(self.request_URL)
            while self.access_token is "":
                time.sleep(5)
            self.shutdown_server()
            # If access token ends with a forward slash
            if self.access_token.endswith("/"):
                self.access_token = self.access_token[:-1]
            print "Access token received: " + self.access_token
            token_file = open(self.access_token_dir, "w")
            token_file.write(self.access_token)
            token_file.close()

        token_file = open(self.access_token_dir, "r")
        self.access_token = token_file.read()

    # Method for subscribing to groups
    def subscribe(self, groupid):

        data = """
    [
      {
        "channel":"/meta/subscribe",
        "clientId":\""""+self.clientId+"""\",
        "subscription":"/group/"""+groupid+"""\",
        "id":"""+str(self.requestid)+""",
        "ext":
          {
            "access_token":\""""+self.access_token+"""\",
            "timestamp":\""""+str(int(time.time()))+"""\"
          }
      }
    ]
    """

        r = requests.post('https://push.groupme.com/faye', data=data, json=None, verify=self.cacert,
                          headers={'content-type': 'application/json'})
        print r.text
        self.increment_request_id()

    # Method for connecting to GroupMe API servers and waiting for messages
    def connect(self):
        ws = websocket.create_connection("wss://push.groupme.com/faye",
                    sslopt={"check_hostname": False, "cert_reqs": ssl.CERT_NONE, "ca_certs": "cacert.pem"})
        print "\nConnecting socket:"
        data = """
    [
      {
        "channel":"/meta/connect",
        "clientId":\""""+self.clientId+"""\",
        "connectionType":"websocket",
        "id":\""""+str(self.requestid)+"""\"
      }
    ]
    """
        print data
        ws.send(data)
        print "Sent"
        print "Receiving..."
        while 1:
            result = ws.recv()
            r = json.loads(result)
            # If websocket message is for a new message
            if "data" in r[0] and r[0]["data"]["type"] == "line.create":
                print "Notifying..."
                notify("GroupMe", r[0]["data"]["alert"])
            print r

    # Method for getting a list if group id's
    def groups(self):
        group_list = []
        url = "https://api.groupme.com/v3/groups?per_page=500&access_token="+self.access_token
        print "Getting list of groups"
        print "Sent (GET): "+url
        r = requests.get(url, verify=self.cacert, headers={'content-type': 'application/json'})
        p = json.loads(r.text)
        r = p["response"]
        for groupid in r:
            group_list.append(groupid["id"])
        print "List of groups: %s\n" % group_list
        return group_list

    # Method to subscribe to messages from all my channels
    def user_subscribe(self):
        data = """
    [
      {
        "channel":"/meta/subscribe",
        "clientId":"%s",
        "subscription":"/user/%s",
        "id":"%s",
        "ext":
          {
            "access_token":"%s",
            "timestamp":%s
          }
      }
    ]
    """ % (self.clientId, self.userid, self.requestid, self.access_token, int(time.time()))
        print data
        r = requests.post('https://push.groupme.com/faye', data=data, json=None, verify=self.cacert,
                          headers={'content-type': 'application/json'})
        # Increase id
        self.increment_request_id()
        # p = json.loads(r.text)
        print r.text

    # Method to get user details
    def user_details(self):
        url = "https://api.groupme.com/v3/users/me?access_token="+self.access_token
        print "Getting user info"
        print "Sent (GET): "+url
        r = requests.get(url, verify=self.cacert, headers={'content-type': 'application/json'})
        p = json.loads(r.text)
        self.userid = p["response"]["id"]
        print "Successfully got user details"

    # Method to increase the request id for every request to GroupMe
    def increment_request_id(self):
        self.requestid += 1

    # Method to start server to capture access token
    def startserver(self):
        print "Server started"
        handler = GetHandler
        self.server = SocketServer.TCPServer(("", self.PORT), handler)
        thread = threading.Thread(target=self.server.serve_forever)
        thread.deamon = True
        thread.start()

    # Method to shutdown SimpleHTTPServer after access token received
    def shutdown_server(self):
        self.server.shutdown()


class GetHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print "GET request captured: " + self.path
        if self.path.startswith('/?access_token'):
            GroupMe.access_token = self.path.split("=", 1)[1]
