import udSDK
import json
import ctypes
class udServerAPI():
  def __init__(self, context :udSDK.udContext):
    self._udServerAPI_Query = udSDK.udExceptionDecorator(udSDK.udSDKlib.udServerAPI_Query)
    self._udServerAPI_ReleaseResult = udSDK.udExceptionDecorator(udSDK.udSDKlib.udServerAPI_ReleaseResult)
    self.context = context

  def Query(self, apiAddress:str, request:str):
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

if __name__ =="__main__":
  udSDK.LoadUdSDK("")
  context = udSDK.udContext()
  context.log_in_interactive()
  s = udServerAPI(context)
  j = s.Query("_user/whoami", None)
  pass

