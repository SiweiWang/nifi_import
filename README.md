# Populate Apach NIFI

## Simple python script to populate the nifi templates and create instance of each Templates on the canvas using nifi Rest API

The propose of this script is to help nifi with CI/CD pipeline to deploy template.

## Support

nifi-api 1.1.1

### How to use

1. clone this repo

2. `python populate.py <NIFI_Server_IP> <NIFI_Server_Port> <NIFI_Template_Dir> <REMOVE_AFTER_CREATED>`

NIFI_Server_IP -- the ip address/hostname of nifi server **required**

NIFI_Server_Port -- the port of the nifi server **required**

NIFI_Template_Dir -- the directory of the nifi template **required**

REMOVE_AFTER_CREATED -- boolean value to allow template removal after instances are created **optional, default to false**

for example `python populate.py 192.168.3.10 8080 ./templates true`

this command will import all the template under `./templates` to nifi api located at http://192.168.3.10:8080/nifi-api. It will also remove the templates after instances are created.

### Python version

2.7

## TODO

Support jinjia templating language for nifi templates.

Support SSL

Better logging message

### License

MIT