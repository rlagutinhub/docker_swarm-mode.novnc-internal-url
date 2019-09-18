#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# NAME:   DOCKER.NOVNC.LISTING.SRV.URL.PY
# DESC:   GEN HTML WITH LISTING DOCKER SERVICES URL
# DATE:   17-09-2019
# LANG:   PYTHON 3
# AUTHOR: LAGUTIN R.A.
# EMAIL:  RLAGUTIN@MTA4.RU

# Examples:
#     /usr/bin/python3 /app/docker.novnc.listing.srv.url.py -p <path-to-properties-file> -o <path-to-output-file> -m [w|1]

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


# Var
mode = False
output = False
properties = False

# Const
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

            # print(json.dumps(col_tasks, indent=4))
            return col_tasks

        else:
            return None


def check_url(url):

    if not url:
        return False

    print(url)

    requests.packages.urllib3.disable_warnings()

    try:
        request = requests.get(url, timeout=10, verify=False)
        # if request.status_code == 200:
        #     print('Web site exists')
        # else:
        #     print('Website returned response code: {code}'.format(code=request.status_code))
        return request.status_code

    except:
        # print('Web site does not exist')
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
        # service_labels = service.get_labels()
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

        if service_name.lower() == srv_name.lower():

            service_col_tmp = dict()

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

    # os.chmod(scrpath, 0o777)

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
        "<meta charset='utf-8' http-equiv='refresh' content='10'>" \
        "<title>Listing docker services url</title>" \
        "<style type='text/css'>" \
        "body {background-color: white; text-align: left; padding: 50px; font-family: 'Open Sans','Helvetica Neue', Helvetica, Arial, sans-serif;}" \
        "a {color: #0066CC; text-decoration:none;}" \
        "a:hover {color: black}" \
        "table {width: 100%; margin: 0px; padding: 0px; border-collapse: collapse; border: 1px solid #F0F4FF;}" \
        "th {font-weight:bold; background-color: #F0F4FF; color: #0066CC; border: 1px solid #F0F4FF; margin: 10px; padding: 7px; text-align: center;}" \
        "td {background-color: white; border: 1px solid #F0F4FF; margin: 10px; padding: 10px; text-align: left;}" \
        "td:first-child {width: 80%; text-align: left;}" \
        "</style>" \
        "</head>" \
        "<body>"
    
    html += "<h2>Listing docker services url</h2>"
    html += "<br><hr><br><center>"

    html += "<table>" \
        "<tr><td><b>URL</b></td><td><b>RESPONSE CODE</b></td></tr>"

    for propertie in properties_data:
    
        service_data = service_get(propertie["srv_name"], propertie["proto"], propertie["port"], propertie["url_appned"])

        html += "<tr><th colspan='2'>{srv_name}</th></tr>".format(srv_name=propertie["srv_name"])

        if service_data:

            for service_task in service_data:
                url_str = str(service_task["proto"]) + '//' + str(service_task["task"]) + '.' + str(service_task["slot"]) + '.' + str(service_task["id"]) + ':' + str(service_task["port"]) + str(service_task["url_appned"])
                url_status = check_url(url_str)

                if url_str and url_status:

                    html += "<tr>"
                    html += "<td><a href='{url_str}' target='_blank'>{url_str}</a></td>".format(url_str=url_str)

                    if url_status == 200:
                        html += "<td><font color=green>{url_status}</font></td>".format(url_status=url_status)
                    else:
                        html += "<td><font color=red>{url_status}</font></td>".format(url_status=url_status)

                    html += "</tr>"

    html += "</table>"

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
        print('docker.novnc.listing.srv.url.py -p <path-to-properties-file> -o <path-to-output-file> -m [w|1]')
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
