import requests
import json
import sys
import pathlib
import xml.etree.ElementTree as ET
import argparse
import os
from jinja2 import Template

# Get command args
parser = argparse.ArgumentParser(description='Deploy templates to secured nifi cluster')
parser.add_argument('--hostname', metavar='hostname', dest="hostname", type=str, required=True,
                    help="nifi cluster hostname")
parser.add_argument('--port', metavar='port', type=str, dest="port", required=True, help="nifi cluster ports")
parser.add_argument('--template-dir', metavar='template dir', type=str, dest="template_dir", required=True,
                    default="./template", help="the dir that contains nifi templates (default to ./template)")
parser.add_argument('--cert-file', metavar='path to cert file', type=str, dest="cert_file", required=False,
                    default="./certs/nifi.cer", help="the path to the cert file (default to ./certs/nifi.cer)")
parser.add_argument('--username', metavar='username', type=str, dest="username", required=False,
                    help="username to login to nifi cluster")
parser.add_argument('--password', metavar='password', type=str, dest="password", required=True,
                    help="password to login to nifi cluster")
parser.add_argument('--delete-after-create', metavar='delete after create', type=str, dest="remove_after_create",
                    required=False, default=True, help="Delete template after it has been instantiated")

args = parser.parse_args()

hostname = args.hostname
port = args.port
template_dir = args.template_dir
remove_after_create = args.remove_after_create
username = args.username
password = args.password
cert_file = args.cert_file

host_url = "https://" + hostname + ":" + port + "/nifi-api"

print("Host ip is {0} port is {1} and the host URL is {2}".format(hostname, port, host_url) )


def get_root_resource_id():
    # URL to get root process group information
    resource_url = host_url + "/flow/process-groups/root"

    auth_header = {'Authorization': 'Bearer ' + get_auth_token()}
    response = requests.get(resource_url, headers=auth_header, verify=False, proxies={'https': ''})

    if not response.status_code == 200:
        print(response)
        print(response.content)
    json = response.json()
    resource_id = json["processGroupFlow"]["id"]
    print(resource_id)
    return resource_id


# print out the name of the template
def get_template_name(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return root[2].text


# upload the template from local to remote nifi cluster
def upload_template(template_file_name):
    upload_url = host_url + "/process-groups/" + get_root_resource_id() + "/templates/upload"
    print (upload_url)
    file_string = open(template_dir+ "/" + template_file_name, 'r').read()


    # using jinjia template

    #template = Template(file_string)
    # rendered= template.render(password=os.environ['es_password'])
    # multipart_form_data = {
    #   'template': rendered,
    # }

    multipart_form_data = {
      'template': file_string,
    }
    auth_header = {'Authorization': 'Bearer ' + get_auth_token()}
    response = requests.post(upload_url, files=multipart_form_data, headers= auth_header, verify=cert_file, proxies={'https': ''})
    print (response)


# create an instance using the template id
def instantiate_template(template_file_name, originX, originY):
    create_instance_url = host_url + "/process-groups/" + get_root_resource_id() + "/template-instance"
    payload = {"templateId": get_template_id(template_file_name), "originX": originX, "originY": originY}
    originX = originX + 600
    originY = originY - 50
    auth_header = {'Authorization': 'Bearer ' + get_auth_token()}
    response = requests.post(create_instance_url, json=payload, headers= auth_header, verify=cert_file, proxies={'https': ''})
    handle_error(create_instance_url, response)


# get list of templates that used for searching template id
def get_templates():
    get_template_instance_url = host_url + "/flow/templates"
    auth_header = {'Authorization': 'Bearer ' + get_auth_token()}
    response = requests.get(get_template_instance_url,  headers= auth_header, verify=cert_file, proxies={'https': ''})
    handle_error(get_template_instance_url, response)
    json = response.json()
    templates = json["templates"]
    return templates


# get the id of the template that matches the name of the saved template
def get_template_id(template_file_name):
    templates = get_templates()
    template_id = ""
    for template in templates:
        print(template)
        print(template_file_name)
        if get_template_name(template_dir + "/" + template_file_name) == template["template"]["name"]:
            print ("Creating instance of " + template["template"]["name"] + " ...")
    template_id = template["template"]["id"]
    return template_id


# removes a template from nifi cluster by its id.
def remove_template(template_id):
    if template_id != "":
        delete_template_url = host_url + "/templates/" + template_id
        auth_header = {'Authorization': 'Bearer ' + get_auth_token()}
        response = requests.delete(delete_template_url, headers= auth_header, verify=cert_file, proxies={'https': ''})
        handle_error(delete_template_url, response)
    else:
        raise SystemError("Can not remove template without a template id")


# check current user session if any
def check_current_user():
    current_user_url = host_url + "/flow/current-user"
    auth_header = {'Authorization': 'Bearer ' + get_auth_token()}
    print(current_user_url)
    res = requests.get(current_user_url, headers=auth_header, verify=cert_file, proxies={'https': ''})
    handle_error(current_user_url, res)


# get authentication token(JWT token) using username and password
def get_auth_token() -> str:
    auth_token_url = host_url + "/access/token"
    res = requests.post(auth_token_url, data={'username': username, 'password': password}, verify=cert_file, proxies={'https': ''})
    handle_error(auth_token_url, res)
    return res.text


# Check and raise exception for a given
def handle_error(endpoint, res):
    if not res.status_code == 200 and not res.status_code == 201:
        raise SystemError("Expect {0} call return either 200 or 401 but got status code {1} with response {2}".format(endpoint, res.status_code, res.text))


# deploys a template to nifi for a specified location
def deploy_template(template_file, origin_x, origin_y):
    remove_template(get_template_id(template_file.name))
    upload_template(template_file.name)
    instantiate_template(template_file.name, origin_x, origin_y)
    if remove_after_create == "true":
        remove_template(get_template_id(template_file.name))


# main function starts here
def main():

    # start up position
    origin_x = 661
    origin_y = -45

    # Make sure current user login is okay
    check_current_user()

    for template_file in pathlib.Path(template_dir).iterdir():
        if template_file.is_file():
            deploy_template(template_file, origin_x, origin_y)


if __name__ == "__main__":
    main()
