# Hue Bulb Replacer
Script for easily replacing a philips hue bulb. Automatically copies the Group/Zone and Scene data from an old bulb to new. Also automatically migrates the name of the old bulb to new.

## Required Preparation
- You'll need both your bridge's local IP address, and an API key (aka a 'username'). You can find instructions on how to get these here: https://developers.meethue.com/develop/get-started-2/
- Add the IP address and username to the bridge_info.py file
- Search and add the new bulb to the hue bridge before running the script. Don't add it to any groups or scenes yet. You may want to rename the new bulb in the hue app to something like 'new bulb' to make it easier to find in the list while running the script.

### Required Libraries
- requests
