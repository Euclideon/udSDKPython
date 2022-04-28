import udSDK
import udGeometry
udSDK.LoadUdSDK()

sphere = udGeometry.udGeometrySphere((0,0,0), 1)
obb = udGeometry.udGeometryOBB((0,0,0,), (1,1,1), (0,0,0))
