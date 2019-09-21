#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# NAME:   DOCKER-SERVICES.INTERNAL-URL.PY
# DESC:   GENERATE HTML WITH LISTING DOCKER SERVICES INTERNAL URL
# DATE:   21-09-2019
# LANG:   PYTHON 3
# AUTHOR: LAGUTIN R.A.
# EMAIL:  RLAGUTIN@MTA4.RU

# Examples:
#     /usr/bin/python3 /app/docker-services.internal-url.py -p <path-to-properties-file> -o <path-to-output-file> -m [w|1]

# Properties:
# [
#     {"srv_name": "hello1", "proto": "http", "port": "8000", "url_appned": "/"},
#     {"srv_name": "hello2", "proto": "http", "port": "8000", "url_appned": "/"},
#     {"srv_name": "hello3", "proto": "https", "port": "8000", "url_appned": "/"}
# ]

import os
import sys
import json
import time
import getopt
import docker
import requests


mode = False
output = False
properties = False

CONF_TIMEOUT = 60


class DockerServiceClass(object):

    def __init__(self, srv_id):

        self.srv = client.services.get(srv_id)

    def get_id(self):

        return self.srv.id

    def get_name(self):

        return self.srv.name

    def get_mode(self):

        return self.srv.attrs['Spec']['Mode']

    def get_tasks(self):

        col_task = dict()
        net_task = dict()
        col_tasks = list()
        tasks = self.srv.tasks()
        # print(json.dumps(tasks, indent=4))

        if tasks:

            for task in tasks:

                if task['Status']['State'] == 'running':

                    col_task['Timestamp'] = task['Status']['Timestamp']
                    col_task['State'] = task['Status']['State']

                    try:
                        col_task['PID'] = task['Status']['ContainerStatus']['PID']
                    except KeyError:
                        col_task['PID'] = 'None'

                    col_task['ContainerID'] = task['Status']['ContainerStatus']['ContainerID']
                    col_task['NodeID'] = task['NodeID']

                    # mode replicated - container DNS name = srv.name.Slot.ID
                    # mode global - container DNS name = srv.name.NodeID.ID (Slot None)

                    try:
                        col_task['Slot'] = task['Slot']
                    except KeyError:
                        col_task['Slot'] = 'None'

                    col_task['Task_ID'] = task['ID']
                    col_task['Task_Ver'] = task['Version']['Index']

                    col_task['NetworksAttachment'] = []

                    for net in task['NetworksAttachments']:
                        net_task['Net_ID'] = net['Network']['ID']
                        net_task['Net_Index'] = net['Network']['Version']['Index']
                        net_task['Net_Scope'] = net['Network']['Spec']['Scope']
                        net_task['Net_Name'] = net['Network']['Spec']['Name']

                        try:
                            net_task['Net_DrvName'] = net['Network']['Spec']['DriverConfiguration']['Name']
                        except KeyError:
                            net_task['Net_DrvName'] = 'None'

                        net_task['Net_Addr'] = net['Addresses']

                        col_task['NetworksAttachment'].append(net_task.copy())
                        net_task.clear()

                    col_tasks.append(col_task.copy())
                    col_task.clear()

            return col_tasks

        else:
            return None


def check_url(url):

    if not url:
        return False

    requests.packages.urllib3.disable_warnings()

    try:
        request = requests.get(url, timeout=10, verify=False)

        # if request.status_code == 200:
        #     print('Web site exists')
        # else:
        #     print('Website returned response code: {code}'.format(code=request.status_code))

        print('{code}: {url}'.format(code=request.status_code, url=url))
        return request.status_code

    except:
        # print('Web site does not exist')

        print('{code}: {url}'.format(code='404', url=url))
        return 404

def services_id():

    service_col = list()

    for service in client.services.list():

        service_col.append(str(service.id))

    return service_col

def service_get(srv_name, proto, port, url_appned):

    service_col = list()

    if not srv_name or not proto or not port or not url_appned:
        return False

    for service_id in services_id():

        service = DockerServiceClass(service_id)
        service_name = service.get_name()
        service_tasks = service.get_tasks()
        service_mode = service.get_mode()

        if list(service_mode.keys())[0] == 'Replicated':
            if service_mode['Replicated']['Replicas'] > 0:
                service_mode_check = 'Replicated'

            else:
                service_mode_check = False

        elif list(service_mode.keys())[0] == 'Global':
            service_mode_check = 'Global'

        else:
            service_mode_check = False

        if service_name.lower() == srv_name.lower() and service_mode_check:

            service_col_tmp = dict()

            if service_tasks:

                for service_task in service_tasks:

                    service_col_tmp['task'] = service_name

                    if service_mode_check == 'Replicated':
                        service_col_tmp['slot'] = service_task['Slot']
                    elif service_mode_check == 'Global':
                        service_col_tmp['slot'] = service_task['NodeID']

                    service_col_tmp['id'] = service_task['Task_ID']
                    service_col_tmp['proto'] = proto
                    service_col_tmp['port'] = port
                    service_col_tmp['url_appned'] = url_appned

                    service_col.append(service_col_tmp.copy())
                    service_col_tmp.clear()

                return service_col

    return False

def output_gen(data, file):

    with open(file, 'wt') as f:
        f.write(data)

    # os.chmod(file, 0o777)

    if os.path.exists(file) and os.path.isfile(file):
        return True

    else:
        return False

def configure():

    with open(properties, 'rt') as f:
        properties_load = f.read()

    try:
        properties_data = json.loads(properties_load)

    except:
        print('Error:', properties)
        sys.exit(1)

    html = "<html>" \
        "<head>" \
        "<meta charset='utf-8' http-equiv='refresh' content='30'>" \
        "<title>Listing docker services internal url</title>" \
        "<style type='text/css'>" \
        "body {background-color: #F5F5F5; text-align: left; padding-left: 50px; padding-right: 50px; font-family: 'dejavu sans light', 'courier new';}" \
        "a {color: #000000; text-decoration:none;}" \
        "a:hover {color: #000000}" \
        "table {width: 100%; margin: 0px; padding: 0px; border-collapse: collapse; border: 1px solid #7499FF;}" \
        "th {font-weight:bold; background-color: #7499FF; color: #000000; border: 1px solid #7499FF; margin: 10px; padding: 10px; text-align: center;}" \
        "td {background-color: white; border: 1px solid #7499FF; margin: 10px; padding: 10px; text-align: left;}" \
        "td:first-child {width: 85%; text-align: left;}" \
        "td.link_ok:hover {background-color: #6EE570;}" \
        "td.link_err:hover {background-color: #E97659;}" \
        "hr {height: 12px; border: 0; box-shadow: inset 0 15px 12px -11px rgba(0,0,0,0.15);}" \
        "#head {width: 100%; height: 60px; position: fixed; top: 0px; left: 56px; background: #F5F5F5;}" \
        "#content {margin-top: 60px;}" \
        "</style>" \
        "</head>" \
        "<body>"
    
    html += "<div id='head'><h2>Listing docker services internal url</h2>" \
        "</div><center>"

    html += "<div id='content'><hr><table>" \
        "<tr><td><b>URL</b></td><td><b>RESPONSE CODE</b></td></tr>"

    for propertie in properties_data:
    
        service_data = service_get(propertie["srv_name"], propertie["proto"], propertie["port"], propertie["url_appned"])

        html += "<tr><th colspan='2'>{srv_name}</th></tr>".format(srv_name=propertie["srv_name"])

        if service_data:

            for service_task in service_data:
                url_name = str(service_task["proto"]) + '://' + str(service_task["task"]) + '.' + str(service_task["slot"]) + '.' + str(service_task["id"]) + ':' + str(service_task["port"]) + str(service_task["url_appned"])
                url_path = str(service_task["proto"]) + '://' + str(service_task["task"]) + '.' + str(service_task["slot"]) + '.' + str(service_task["id"]) + ':' + str(service_task["port"]) + str(service_task["url_appned"])
                url_status = check_url(url_path)

                if url_name and url_path and url_status:

                    if url_status == 200:
                        html += "<tr>"
                        html += "<td class=link_ok><a href='{url_path}' target='_blank'>{url_name}</a></td>".format(url_path=url_path, url_name=url_name)
                        html += "<td><font color=green>{url_status}</font></td>".format(url_status=url_status)
                    else:
                        html += "<tr>"
                        html += '<td class=link_err><a href="{url_path}" target="_blank">{url_name}</a></td>'.format(url_path=url_path, url_name=url_name)
                        html += "<td><font color=red>{url_status}</font></td>".format(url_status=url_status)

                    html += "</tr>"

    html += "</table></div>"
    html += "</center><br>" \
        "</body>" \
        "</html>"

    if not output_gen(html, output):
        print('Error:', output)
        sys.exit(1)

def loop():

    try:
        while True:
            configure()
            time.sleep(int(CONF_TIMEOUT))

    except KeyboardInterrupt:
        pass

def main():

    global mode
    global output
    global properties

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:o:m:', ['properties=','output=','mode='])

    except getopt.GetoptError:
        pass

    # print('argv: ', sys.argv[1:])
    # print('opts: ', opts)

    try:
        for opt, arg in opts:
            if opt in ('-p', '--properties'):
                if os.path.isfile(arg):
                    properties = arg

            elif opt in ('-o', '--output'):
                if os.path.isdir(os.path.dirname(arg)):
                    output = arg

            elif opt in ('-m', '--mode'):
                mode = arg

    except NameError:
        pass

    if not properties or not output or not mode in ('wait', 'once', 'w', '1'):
        print('./docker-services.internal-url.py -p <path-to-properties-file> -o <path-to-output-file> -m [w|1]')
        sys.exit(1)

    # print('properties:', properties)
    # print('output    :', output)
    # print('mode      :', mode)
    
    if mode == 'wait' or mode == 'w':
        loop()

    elif mode == 'once' or mode == '1':
        configure()


if __name__ == '__main__':

    try:
        # client = docker.from_env()
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    except OSError as e:
        print('Error:', e)
        sys.exit(1)

    sys.exit(main())
