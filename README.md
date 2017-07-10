# Populate Apach NIFI

## Simple python script to populate the nifi templates and create instance of each Templates on the canvas using nifi Rest API

The propose of this script is to help nifi with CI/CD pipeline to deploy template.

## Support

nifi-api 1.1.1

### How to use

1. clone this repo

2. `populate.py [-h] --hostname, --port, --template-dir, --username username, --password password`

for example `python populate.py 192.168.3.10 8080 ./templates --username nifi --password password`

this command will import all the template under `./templates` to nifi api located at http://192.168.3.10:8080/nifi-api. It will also remove the templates after instances are created.

### Python version

3.6

## TODO
Support SSL verification

### License

MIT