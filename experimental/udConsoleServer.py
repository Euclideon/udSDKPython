import socketserver
import struct
import camera
global matrix
#=[1, 0, 0, 0,
         #0, 1, 0, 0,
         #0, 0, 1, 0,
         #0, 0, 0, 1]

class udStreamCommServer(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        #print("{} wrote:".format(self.client_address[0]))
        #print(self.data)
        matrix = sendCamera.matrix.flatten()
        # just send back the same data, but upper-cased
        data = struct.pack('<16d',*matrix)
        #print(f"Sent {data}")
        #matrix[14] += 0.001
        self.request.sendall(data)
        #self.request.sendall(self.data.upper())

def sync_camera(camera: camera.Camera):
    HOST, PORT = "10.10.0.84", 447
    global sendCamera
    sendCamera = camera
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), udStreamCommServer) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
