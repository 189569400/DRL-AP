import os
import sys
import csv
import json
import random
from random import choice
from jinja2 import Environment, select_autoescape, FileSystemLoader

REAL_ATTACK_TOPOLOGY_TEMPLATE_PATH="../MulVal_P/Template_P/"
REAL_ATTACK_TOPOLOGY_TEMPLATE_NAME="attack_temp_v1.P"
REAL_ATTACK_TOPOLOGY_TEMPLATE_VERSION='v1'

env = Environment(loader=FileSystemLoader(REAL_ATTACK_TOPOLOGY_TEMPLATE_PATH), autoescape=select_autoescape('P'))
template = env.get_template(REAL_ATTACK_TOPOLOGY_TEMPLATE_NAME)

def read_vul_info():
    info_list = []
    vul_file = open("vul_info.txt")
    for line in vul_file:
        line = line.strip('\n')
        info_list.append(line)
    vul_file.close()
    return info_list

def read_scan_config():
    host_list = []
    ip_list = []
    with open('scan_config.csv', 'r') as csvfile:
        csv_read = csv.reader(csvfile)
        for i in csv_read:
            host_list.append(i[0])
            ip_list.append(i[1])
    return host_list, ip_list

def deJsonTop_v1(webTemp, fileTemp):
    baiscFile = open('./attack.P', 'w')
    attack_temp = template.render(CVE_Id_Web=webTemp[2], Web_Module=webTemp[1], Web_Transport=webTemp[1], 
                                            Web_Port=webTemp[1], Web_Product=webTemp[1], 
                                            CVE_Id_File=fileTemp[2], File_Module=fileTemp[0], 
                                            File_Transport=fileTemp[1], File_Port=fileTemp[1])

    #Write to .P
    baiscFile.write(attack_temp)
    baiscFile.close()  

    print("Generate scan topology v1 P file successfully")

def deJsonTop_v2(webTemp, fileTemp, fireTemp):
    baiscFile = open('./attack.P', 'w')
    attack_temp = template.render(CVE_Id_Web=webTemp[2], Web_Module=webTemp[1], Web_Transport=webTemp[1], 
                                            Web_Port=webTemp[1], Web_Product=webTemp[1], 
                                            CVE_Id_File=fileTemp[2], File_Module=fileTemp[0], 
                                            File_Transport=fileTemp[1], File_Port=fileTemp[1],
CVE_Id_Fire=fireTemp[2], Fire_Module=fireTemp[0], Fire_Transport=fireTemp[1], Fire_Port=fireTemp[1])

    #Write to .P
    baiscFile.write(attack_temp)
    baiscFile.close()  

    print("Generate scan topology v2 P file successfully")


if __name__ == "__main__":
    webTemp = []
    fileTemp = []
    fireTemp = []
    host_list = read_scan_config()[0]
    ip_list = read_scan_config()[1]
    count_ip = 0

    for host in host_list:
        print("Run Nmap on target '{}' ({})...".format(host, ip_list[count_ip].strip()))
        if host == 'webServer':
            os.system('sudo nmap -p -sV -oX --version-all --script vuln ' + ip_list[count_ip] + ' -oN nmap.txt')
            status = os.system('python2 decode_nmap.py')
            if os.WEXITSTATUS(status) != 0:
                print("ERROR: Nmap encountered a problem")
                sys.exit(1)
            webTemp = read_vul_info()
        if host == 'fileServer':
            os.system('sudo nmap -p -sV -oX --version-all --script vuln ' + ip_list[count_ip] + ' -oN nmap.txt')
            status = os.system('python2 decode_nmap.py')
            if os.WEXITSTATUS(status) != 0:
                print("ERROR: Nmap encountered a problem")
                sys.exit(1)
            fileTemp = read_vul_info()
        if host == 'fireWall':
            os.system('sudo nmap -p -sV -oX --version-all --script vuln ' + ip_list[count_ip] + ' -oN nmap.txt')
            status = os.system('python2 decode_nmap.py')
            if os.WEXITSTATUS(status) != 0:
                print("ERROR: Nmap encountered a problem")
                sys.exit(1)
            fireTemp = read_vul_info()
        count_ip = count_ip + 1

    if REAL_ATTACK_TOPOLOGY_TEMPLATE_VERSION == 'v1':    
        deJsonTop_v1(webTemp, fileTemp)
    if REAL_ATTACK_TOPOLOGY_TEMPLATE_VERSION == 'v2':
        deJsonTop_v2(webTemp, fileTemp, fireTemp)