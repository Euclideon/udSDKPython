"""
Basic example of sending a request to the udCloud server using udServerAPI. Returned is a json response from the server
"""
import udSDK
from udSDKServerAPI import udServerAPI
import sampleLogin
if __name__ == "__main__":
  udSDK.LoadUdSDK("")
  context = udSDK.udContext()
  sampleLogin.log_in_sample(context)
  # test basic whoami request:
  s = udServerAPI(context)
  j = s.query("_user/whoami", None)
  print(j)
