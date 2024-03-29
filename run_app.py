import subprocess
subprocess.call("pip3 install Werkzeug==2.0.0") # need to downgrade this one for Dash to work
subprocess.call("pip3 install tabulate")


from tabulate import tabulate
import os


print(tabulate([["I want to install dependencies..."],
                ["I want to run OLX scraper..."],
                ["I want to run Dash app..."]],
               showindex="always",
               headers=["Index", "Action"],
               tablefmt="pretty"))

val = input("Please select index of action: ")

if val == "0":
    #os.system("pip3 install -r requirements.txt")
    req = os.path.dirname(__file__) + "\\requirements.txt"
    subprocess.call("pip3 install -r" + req, shell=True)
    input("Load completed. Press ENTER to proceed")

elif val == "1":
    from db import save_in_db

elif val == "2":
    subprocess.call(os.path.dirname(__file__) + "\\db\\app.py", shell=True)
    input("Load completed. Press ENTER to proceed")

else:
    print("Action index is not on the list!")
    input("Press ENTER to proceed")