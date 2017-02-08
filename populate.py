import requests
import json
import sys
import pathlib

# Gets command args
hostname = sys.argv[1]
port = sys.argv[2]
templateDir = sys.argv[3]

print 'Host ip is ' + hostname + ', and port is ' + port
HostURL= "http://" + hostname + ":" + port + "/nifi-api"

# Get the resource group under nifi
resource_url = HostURL + "/resources"
response = requests.get(resource_url)
json = response.json()

resources = json["resources"]
nifi = []

# Random start up position
originX = 661
originY = -45

for resource in resources:
  if "NiFi Flow" == resource["name"]:
    nifi = resource["identifier"].split("/")

resourceId = nifi[2]
print "resource id for nifi flow is " + resourceId

for templateFile in pathlib.Path(templateDir).iterdir():
  if templateFile.is_file():
    print "Adding templates " + templateFile.name + " ..."

    # upload the templates
    upload_url = HostURL + "/process-groups/" + resourceId + "/templates/upload"
    multipart_form_data = {
      'template': open(templateDir+ "/" + templateFile.name, 'rb'),
    }
    response = requests.post(upload_url, files=multipart_form_data)

    # get the template ids
    get_template_instance_url = HostURL + "/flow/templates"
    response = requests.get(get_template_instance_url)
    json = response.json()
    templates = json["templates"]

    templateId = ""
    for template in templates:
      if templateFile.name.split(".")[0] == template["template"]["name"]:
        print "Creating instance of " + templateFile.name.split(".")[0] + " ..."
        templateId = template["template"]["id"]

    # create the template use template id
    create_instance_url = HostURL + "/process-groups/" + resourceId + "/template-instance"
    payload = {"templateId": templateId, "originX": originX, "originY": originY}
    originX = originX + 600
    originY = originY - 50
    response = requests.post(create_instance_url, json=payload)
    print response
    print "Done."

