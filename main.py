# Philips Hue Bulb Replacer Script
# Author: ThioJoe - https://github.com/thiojoe

import requests
import collections
import time
from bridge_info import *


# Checks if bridge info has been added
if (bridge_ip == "CHANGE ME" or username == "CHANGE ME"):
    print("ERROR: You must update bridge_info.py to add your bridge's API.")
    input("Press Enter to exit.")
    exit()

requests.packages.urllib3.disable_warnings()  # Hides insecure SSL warnings from Request

api_url = 'https://' + bridge_ip + "/api/" + username + "/"  # Uses info from bridge_info.py

# Print Instructions
print("---------------------------------   INFO   ---------------------------------")
print(" - This script is used for replacing old hue bulbs that are either broken, or being upgraded.")
print(" - Groups/Zones and Scenes from old bulb will be copied to new, and new bulb will be renamed to the old bulb's name.")
print(" - The old bulb will be renamed to add (old). This script will NOT delete the old bulb.")
print(" - At the end, you will delete the old bulb yourself once you verify everything worked.")
print(" - NOTE: If the bulbs have different color gamuts, the copied scene data may not match 100%, but should be close")
print()

print("--------------------------   REQUIRED PREPARATION   --------------------------")
print(" 1. Make sure you have already added the new bulb to the bridge using the hue app.")
print("    - Do not add new bulb to any scenes or groups until after you run script.")
print("    - Maybe rename new bulb (using hue app) to something like 'new bulb' to make it easy to find in next step")
print(" 2. Add your bridge's IP address, and your hue API key (also called 'username') to bridge_info.py file")
print("    - Instructions for how to generate that info is also in the bridge_info.py file")

input("Press Enter to Begin...")
print()

# Get all info from bridge
r = requests.request("GET", api_url, verify = False).json()

# Gets names and ID numbers of all lights
print("Fetching all lights... Please Wait...")
print()
print("LIGHT NAME    -    LIGHT ID")

# Go through and print dictionary of lights, where key is the light ID number, and value is another dictionary of light info
for id, info in r['lights'].items():
    # Get key from dict light
    name = info['name']
    print("{:20} {}".format(name, id))

# User chooses old light from list
print()
old_light_id = input("From list above, enter ID number of the OLD light to be replaced: ") # Takes input
new_light_id = input("From list above, enter ID number of the NEW light that will inherit the old light's properties: ")

# Get name of chosen light
old_light_name = r['lights'][old_light_id]['name']
new_light_name = r['lights'][new_light_id]['name']
print()
print("Old Light Being Replaced: " + old_light_name)
print("New Light: " + new_light_name)

answer = input("Is this correct? (New bulb will be overwritten) (Y/N): ")
if answer.lower().startswith("n"):
    input("Press Enter to Exit...")
    exit()
elif answer.lower().startswith("y"):
    print("Confirmed. Fetching groups and scenes.")
else:
    print("ERROR: Invalid response. Press enter to exit.")
    exit()


# Check groups with old light
r = requests.request("GET", (api_url + 'groups'), verify = False).json()
group_list = list(r)

groups_with_light = [] # List type variable to contain list of groups that contain the old bulb
for group_index in range(len(group_list)):  # Iterates through all groups returned from API (Note group_index is not same as group's ID. Group_index only exists as for-loop index)
    if old_light_id in r.get(group_list[group_index], {}).get('lights'):
        groups_with_light.append(group_list[group_index])  # If a group contains old_light_id, group's ID is added to list groups_with_light
print("Groups Found with Old Light: " + str(groups_with_light))

# Check scenes with old light
r = requests.request("GET", (api_url + 'scenes'), verify = False).json()
scene_list = list(r)

scenes_with_light = [] # List type variable to contain list of scenes that contain old bulb
for scene_index in range(len(scene_list)):  # Iterates through all scenes returned from API
    if old_light_id in r.get(scene_list[scene_index], {}).get('lights'):
        scenes_with_light.append(scene_list[scene_index])  # If a scene contains old_light_id, scene's ID is added to list scenes_with_light
print("Scenes Found with Old Light: " + str(scenes_with_light))
print()

print("Beginning Data Copy...")
print()

# Add new light to groups
print("Copying Groups... (Step 1/3)")
for index in range(len(groups_with_light)):  # Repeats for all groups found with old light
    group_light_list = [] # Reset group light list to empty
    r = requests.request("GET", (api_url + 'groups/' + groups_with_light[index] ), verify = False).json() # Calls API for specific group
    group_light_list = r.get("lights", {}) # Acquires list of lights in group
    group_light_list.append(new_light_id) # Adds new light ID to list
    payload = {'lights': group_light_list}
    r = requests.request("PUT", (api_url + 'groups/' + groups_with_light[index] ), json=payload, verify = False)  # Sends back list of lights with new light added
    time.sleep(0.25)

# Get lightstates for old light in every scene and duplicate lightstate to new light's id within each scene
print("Copying Scenes... (Step 2/3)")
for index in range(len(scenes_with_light)):
    r = requests.request("GET", (api_url + 'scenes/' + scenes_with_light[index]), verify = False).json()
    old_light_state = (r.get("lightstates", {}).get(old_light_id))
    r = requests.request("PUT", (api_url + 'scenes/' + scenes_with_light[index] + '/lightstates/' + new_light_id ), json=old_light_state, verify = False)
    time.sleep(0.25)
time.sleep(1)

# Rename old bulb
print("Renaming Bulbs... (Step 3/3)")
old_light_rename = old_light_name + " (old)"
payload = {'name': old_light_rename}
requests.request("PUT", (api_url + 'lights/' + old_light_id), json=payload, verify = False)

# Rename new bulb
payload = {'name': old_light_name} # USE VERSION
requests.request("PUT", (api_url + 'lights/' + new_light_id), json=payload, verify = False)

print()
r = requests.request("GET", (api_url + 'lights'), verify = False).json()
if r.get(old_light_id, {}).get('name') == old_light_rename:
    print("Old Bulb Renamed to: " + old_light_rename)
if r.get(new_light_id, {}).get('name') == old_light_name:
    print("New Bulb Renamed to: " + old_light_name)

print()
print("Check to make sure new light has been added, and test each scene to ensure new bulb behaves as expected.")
print("If everything looks good, you can delete the \"(old)\" light using the hue app.")
print()
input("Press Enter to Exit...")