"""
convenience for setting API key (if applicable) to prevent needing to
"""
API_KEY =None
server = "https://udcloud.euclideon.com"

def log_in_sample(context):
  if API_KEY is not None:
    context.connect_with_key(API_KEY, server, "Python Samples", "0.1")
  else:
    context.log_in_interactive(serverPath=server, appName="Python Samples", appVersion="0.1")