import ctypes
import json

import udSDK


class udServerAPI():
  """
  Represents an interface for sending and receiving API calls from a udCloud server
  """
  def __init__(self, context :udSDK.udContext):
    self._udServerAPI_Query = udSDK.udExceptionDecorator(udSDK.udSDKlib.udServerAPI_Query)
    self._udServerAPI_ReleaseResult = udSDK.udExceptionDecorator(udSDK.udSDKlib.udServerAPI_ReleaseResult)
    self.context = context

  def query(self, apiAddress:str, request:str):
    """
    Send query to apiAddress with a payload of request
    """
    pResult = ctypes.c_char_p(0)
    if request is not None:
      request = request.encode('utf8')
    self._udServerAPI_Query(self.context.pContext, apiAddress.encode('utf8'), request, ctypes.byref(pResult))
    if pResult.value is not None:
      res = json.loads(pResult.value.decode('utf8'))
    else:
      res = None
    self._udServerAPI_ReleaseResult(ctypes.byref(pResult))
    return res


