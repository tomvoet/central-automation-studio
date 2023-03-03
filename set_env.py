import os

url = os.environ["API_URL"]
secure = os.environ["SECURE"]

clearpass_url = os.environ["CLEARPASS_URL"]
clearpass_token = os.environ["CLEARPASS_TOKEN"]

if secure == "T" or secure == "True":
	os.environ["SECURE"] = "True"
	print("HTTPS configuration enabled.")
else:
	os.environ["SECURE"] = "False"
	print("HTTP will be used.")

# setting api_url within UI/assets/js/main.js
# NOTE: copyright symbol removed because of encoding issues when trying to read the file
data = ""
with open("/usr/local/apache2/htdocs/assets/js/proxy.js", "r") as f: # read mode
    data = f.read()

data = data.replace("Replace with API URL", url)

with open("/usr/local/apache2/htdocs/assets/js/proxy.js", "w") as f: # write mode
    f.write(data)

print("API_URL: ", os.environ["API_URL"])
print("SECURE: ", os.environ["SECURE"])

clearpass_data = ""

with open("/usr/local/apache2/htdocs/assets/js/main.js", "r") as f: # read mode
	clearpass_data = f.read()

clearpass_data = clearpass_data.replace("Replace with ClearPass URL", clearpass_url)
clearpass_data = clearpass_data.replace("Replace with ClearPass Token", clearpass_token)

with open("/usr/local/apache2/htdocs/assets/js/main.js", "w") as f: # write mode
	f.write(clearpass_data)

print("CLEARPASS_URL: ", os.environ["CLEARPASS_URL"])
print("CLEARPASS_TOKEN: ", os.environ["CLEARPASS_TOKEN"])