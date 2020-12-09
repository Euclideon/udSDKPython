
import udSDK
import udSDKProject
from sys import argv, exit
def test_add_place(project):
    root = project.GetProjectRoot()
    a = root.firstChild
    name = "test"
    lla = [0, 0, 0]
    count = 1
    a.add_place(name, lla, count)
    a.update_place_list()
    p = a.places[-1]
    assert p.name == name
    assert p.count == 1
    for val in range(len(p.lla)):
        assert p.lla[val] == lla[val]


if __name__ == "__main__":
    if len(argv) != 4:
        print(f"Usage: {argv[0]} username password projectFile")
        print("Username: Euclideon Username")
        print("Password: Euclideon Password")
        print("project projectFile: e.g. b8bda426-a3b1-4359-8eed-d8d692928c2e")
        print("download directory")
        exit(0)
    udSDK.LoadUdSDK("")
    context = udSDK.udContext()
    try:
        context.try_resume("https://stg-ubu18.euclideon.com","pythonPlacesTest", argv[1])
    except udSDK.UdException:
        context.Connect("https://stg-ubu18.euclideon.com", "pythonPlacesTest", argv[1], argv[2])
    project = udSDKProject.udProject(context)
    projectFile = argv[3]
    project.LoadFromFile(projectFile)
    #filename = f"{argv[4]}/downloadedProject.json"
    test_add_place(project)

    pass
