import requests
import json
import sys
import pathlib
import xml.etree.ElementTree as ET

# Get command args
hostname = sys.argv[1]
port = sys.argv[2]
templateDir = sys.argv[3]

print 'Host ip is ' + hostname + ', and port is ' + port
HostURL= "http://" + hostname + ":" + port + "/nifi-api"

# Get the resource group under nifi
resource_url = HostURL + "/resources"
print resource_url

response = requests.get(resource_url)
print response.json()
json = response.json()

resources = json["resources"]

def get_root_resource_id():
  nifi = []
  for resource in resources:
    if "NiFi Flow" == resource["name"]:
      nifi = resource["identifier"].split("/")

  resourceId = nifi[2]
  print "resource id for nifi flow is " + resourceId
  return resourceId

resourceId = get_root_resource_id()

# print out the name of the template
def get_template_name(file):
  tree = ET.parse(file)
  root = tree.getroot()
  return root[2].text

# upload the template
def upload_template(template_file_name):
    upload_url = HostURL + "/process-groups/" + resourceId + "/templates/upload"
    print upload_url
    multipart_form_data = {
      'template': open(templateDir+ "/" + template_file_name, 'rb'),
    }
    response = requests.post(upload_url, files=multipart_form_data)
    print response

def instantiate_template(template_file_name, originX, originY):
    # create an instance using the template id
    create_instance_url = HostURL + "/process-groups/" + resourceId + "/template-instance"
    print create_instance_url
    payload = {"templateId": get_template_id(get_templates(), template_file_name), "originX": originX, "originY": originY}
    originX = originX + 600
    originY = originY - 50
    response = requests.post(create_instance_url, json=payload)
    print response
    print "Done."

def get_templates():
    get_template_instance_url = HostURL + "/flow/templates"
    response = requests.get(get_template_instance_url)
    json = response.json()
    templates = json["templates"]
    return templates

# get the template ids
def get_template_id(templates, template_file_name):
    templateId = ""
    for template in templates:
      if get_template_name(templateDir+ "/" + template_file_name) == template["template"]["name"]:
        print "Creating instance of " + template["template"]["name"] + " ..."
        templateId = template["template"]["id"]
        return templateId

def import_templates():
  # Random start up position
  originX = 661
  originY = -45

  for templateFile in pathlib.Path(templateDir).iterdir():

    if templateFile.is_file():
      print "Adding templates " + templateFile.name + " ..."
      upload_template(templateFile.name)
      instantiate_template(templateFile.name, originX, originY)

import_templates()