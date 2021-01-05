import requests
import csv
import pandas as pd
import numpy as np
import time
import sys

baseUrl = "https://api.groupme.com/v3"
token = "b321c8b0313c0139e4074ac2b704d62f"

sheetsUrl = "https://script.google.com/macros/s/AKfycbyuZ9NacL8780uQV5FY01d6Nq4VX_w3odKGIcxxkjtaf1NmHBU5Vir5/exec"

classes = pd.read_csv('./WN2021.csv').to_numpy()

log = open('logs.txt', mode='a')
logVerbose = open('logsVerbose.txt', mode='a')

with open('groupMeList.csv', mode='a') as fRes:
    email_writer = csv.writer(
        fRes, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    email_writer.writerow(
        ["name", "share_url", "share_qr_code_url", "id", "group_id", "thread_id", "phone_number", "type", "creator_user_id"])
    for x in range(0,len(classes)):
        # write to logs
        log.write(str(x))
        log.write(": ")
        log.write(str(classes[x][0]))
        log.write("\n")

        # create GroupMe Api post request
        obj = {
            "name": classes[x][0],
            "share": True,
        }   
        try:
            response = requests.post(baseUrl + "/groups?token=" + token, json = obj)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            x -= 1
            logVerbose.write("ERROR OCCURRED AS EXCEPTION\n")
            logVerbose.write(e)
            logVerbose.write("\n")
            log.write("ERROR OCCURRED AS EXCEPTION\n")
            log.write(e)
            log.write("\n")
            time.sleep(300)
            continue
        logVerbose.write(str(response.json()))
        logVerbose.write("\n")
        k = response.json()

        # if we get rate limited
        if ('meta' in k and k['meta']['code'] != 200 and k['meta']['code'] != 201 and k['meta']['code'] != 202 and k['meta']['code'] != 203):
            log.write("\n")
            log.write("ERROR\n")
            log.write("code: " + str(k['meta']['code']) + "\n")
            log.writelines(k['meta']["errors"])
            log.write("\n")

            x -= 1
            logVerbose.write("ERROR OCCURRED\n\n")
            time.sleep(300)
            continue

        # write to verbose logs
        logVerbose.write(str(k["response"]["share_url"]))
        logVerbose.write("\n")
        logVerbose.write(str((k["response"]["name"])))
        logVerbose.write("\n\n")

        email_writer.writerow([k["response"]["name"], k["response"]["share_url"], k["response"]["share_qr_code_url"], k["response"]["id"], k["response"]["group_id"], k["response"]["thread_id"], k["response"]["phone_number"], k["response"]["type"], k["response"]["creator_user_id"]])

        formData = {
            "name": k["response"]["name"], 
            "share_url": k["response"]["share_url"], 
            "share_qr_code_url": k["response"]["share_qr_code_url"], 
            "id": k["response"]["id"], 
            "group_id": k["response"]["group_id"], 
            "thread_id": k["response"]["thread_id"], 
            "phone_number": k["response"]["phone_number"], 
            "type": k["response"]["type"], 
            "creator_user_id": k["response"]["creator_user_id"],
        }

        requests.post(sheetsUrl, data=formData)
        time.sleep(20)

