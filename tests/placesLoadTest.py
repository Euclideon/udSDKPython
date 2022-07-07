
import udSDK
import udSDKScene
from sys import argv, exit

def test_iterators():
    oldProject = udSDKProject.udProject(context)
    oldProject.load_from_file("D:/git/vaultsdkpython/hospitals.json")
    virus, hospitals, pharmacies = [*oldProject.rootNode.children]


def fix_old_places_project(context:udSDK.udContext):
    oldProject = udSDKProject.udProject(context)
    oldProject.load_from_file("D:/git/vaultsdkpython/hospitals.json")
    rootnode = oldProject.rootNode



    newProject = udSDKProject.udProject(context)
    newProject.create_in_file("hospitals", "D:/git/vaultsdkpython/hospitalsNew.json")
    newRoot = newProject.rootNode
    for set in [*rootnode.children]:
        newSet = newRoot.create_child("Places", set.name)
        newSet.pin = set.pin
        #newSet.pinDistance = set.pinDistance
        #newSet.labelDistance = set.labelDistance
        for p in set:
            lla = (
                p.get_property("lla[0]", float),
                p.get_property("lla[1]", float),
                p.get_property("lla[2]", float),
            )
            newSet.add_item(p.name, lla, p.count)
    newProject.rootNode.set_metadata_int("defaultcrs", 2326)
    newProject.rootNode.set_metadata_int("projectcrs", 4326)
    newProject.save()


def test_create_project(context:udSDK.udContext):
    project = udSDKProject.udProject(context)
    project.create_in_file("test", "projectCreateTest.json")
    root = project.rootNode
    placelayer = root.create_child("Places", "test")
    project.save()
    name = "test"
    crds = [0, 0, 0]
    count = 1
    placelayer.add_item(name, crds, count)
    project.save()

def test_save_place(project:udSDKProject.udProject, file:str):
    project.save_to_file(file)

def test_add_place(project):
    root = project.rootNode
    a = root.firstChild
    name = "test"
    lla = [0, 0, 0]
    count = 1
    a.add_item(name, lla, count)
    #placeNodes are directly indexable:
    p = a[-1]
    assert p.name == name
    assert p.count == 1
    for val in range(len(p.coordinates)):
        assert p.coordinates[val] == lla[val]


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
        context.connect_legacy("https://stg-ubu18.euclideon.com", "pythonPlacesTest", argv[1], argv[2])
    project = udSDKProject.udProject(context)
    projectFile = argv[3]
    project.load_from_file(projectFile)
    #filename = f"{argv[4]}/downloadedProject.json"
    test_add_place(project)
    #test_create_project(context)
    test_save_place(project, "hospitalsModified.json")

    fix_old_places_project(context)

    pass
