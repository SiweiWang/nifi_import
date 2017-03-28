import requests
import json
import sys
import pathlib
import xml.etree.ElementTree as ET
import os
from jinja2 import Template

# Get command args
hostname = sys.argv[1]
port = sys.argv[2]
templateDir = sys.argv[3]
remove_after_create = sys.argv[4]

print 'Host ip is ' + hostname + ', and port is ' + port
HostURL= "http://" + hostname + ":" + port + "/nifi-api"

# Get the resource group under nifi
resource_url = HostURL + "/resources"
print resource_url

response = requests.get(resource_url)
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
    file_string = open(templateDir+ "/" + template_file_name, 'r').read()
    template = Template(file_string)
    rendered= template.render(password=os.environ['es_password'])
    multipart_form_data = {
      'template': rendered,
    }
    response = requests.post(upload_url, files=multipart_form_data)
    print response

# create an instance using the template id
def instantiate_template(template_file_name, originX, originY):
    create_instance_url = HostURL + "/process-groups/" + resourceId + "/template-instance"
    payload = {"templateId": get_template_id(template_file_name), "originX": originX, "originY": originY}
    originX = originX + 600
    originY = originY - 50
    response = requests.post(create_instance_url, json=payload)
    print response
    print "Done."

# get templates
def get_templates():
    get_template_instance_url = HostURL + "/flow/templates"
    response = requests.get(get_template_instance_url)
    json = response.json()
    templates = json["templates"]
    return templates

# get the template id
def get_template_id(template_file_name):
    templates = get_templates()
    template_id = ""
    for template in templates:
      if get_template_name(templateDir+ "/" + template_file_name) == template["template"]["name"]:

        print "Creating instance of " + template["template"]["name"] + " ..."
        template_id = template["template"]["id"]
    return template_id

def check_and_remove_template(template_id):
  if template_id != "":
    delete_template_url = HostURL + "/templates/" + template_id
    response = requests.delete(delete_template_url)
    print delete_template_url
    print response
    print "deleted template " + template_id

# main function, import templates
def import_templates():
  # random start up position
  originX = 661
  originY = -45

  for templateFile in pathlib.Path(templateDir).iterdir():
    if templateFile.is_file():
      print "importing  templates " + templateFile.name + " ..."
      check_and_remove_template(get_template_id(templateFile.name))
      upload_template(templateFile.name)
      instantiate_template(templateFile.name, originX, originY)
      print remove_after_create
      if remove_after_create == "true":
        check_and_remove_template(get_template_id(templateFile.name))

import_templates()