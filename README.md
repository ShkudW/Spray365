![Spray 365 Logo](screenshots/spray365_logo.png)

<p align="center">
  <a href="https://github.com/MarkoH17/Spray365/releases/latest">
    <img src="https://img.shields.io/github/v/tag/markoh17/spray365?label=latest&style=flat-square">
  </a>
  <a href="https://github.com/MarkoH17/Spray365/stargazers">
    <img src="https://img.shields.io/github/stars/MarkoH17/Spray365?&style=flat-square">
  </a>
  <a href="https://github.com/MarkoH17/Spray365/network/members">
    <img src="https://img.shields.io/github/forks/MarkoH17/Spray365?&style=flat-square">
  </a>
  <a href="https://github.com/MarkoH17/Spray365/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/MarkoH17/Spray365?&style=flat-square">
  </a>
  <a href="https://github.com/MarkoH17/Spray365/blob/main/spray365.py">
    <img src="https://img.shields.io/github/languages/top/markoh17/spray365?style=flat-square">
  </a>
  <br>
</p>

# What's new in this fork??
Spray365 is one of my go-to tools during Red Team engagements. It has proven invaluable on numerous occasions for establishing an initial foothold within an enterprise. I decided to further enhance its capabilities by integrating TOR routing. The primary objective is to maximize operational anonymity and prevent the exposure of my true source IP address.

### New flags:
```
  Tor options:
    -t, --tor                   Send authentication requests through Tor, switching to a new exit IP before everyauthentication attempt
    --tor_proxy                 SOCKS proxy of the Tor service (format: socks5h://tor.address:port)  [default:socks5h://127.0.0.1:9050]
    --tor_control               Address and port of the Tor control service (format: tor.address:port)  [default:127.0.0.1:9051]
    --tor_countries             Comma-separated list of 2 letter country codes to pick Tor exit IPs from (e.g.us,de,gb). Leave unspecified to use any country
```

### Requirements
 - Python
   - 3.9 (minimum)
   - 3.10 (recommended)

### Installation
Clone the repository, install the required Python packages, and run Spray365!
```bash
git clone https://github.com/MarkoH17/Spray365
cd Spray365
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 spray365.py
```

### Configure tor:
## Install tor:
```
sudo apt update
sudo apt install torsocks -y
sudo apt install libtorsocks0 -y
```
## editing tor config file /etc/tor/torrc:
```
ControlPort 9051
CookieAuthentication 1
```
## Create symlink:
```
sudo ln -s /usr/lib/x86_64-linux-gnu/torsocks/libtorsocks.so /usr/lib/x86_64-linux-gnu/libtorsocks.so
```
## sudo systemctl restart tor@default:
```
sudo systemctl restart tor@default
```

### Usage
## Generate ep file (plan)
```
python3 spray365.py generate normal -ep Spray_Plan --delay 40 -d domain.com -u valid_UserAccount.txt  -p 'Aa123456' -rUA
```

## use TOR
```
python3 spray365.py spray -ep Spray_Plan -t --tor_countries il,us
```



## Spray365 Usage

<details>
  <summary>Generate Mode (Normal)</summary>
  
  ```
Usage: spray365.py generate normal [OPTIONS]

  Generate a vanilla (normal) execution plan

Options:
  -ep, --execution_plan           File path where execution plan should be saved  [required]
  -d, --domain                    Office 365 domain to authenticate against  [required]
  --delay                         Delay in seconds to wait between authentication attempts  [default: 30]
  -mD, --min_loop_delay           Minimum time to wait between authentication attempts for a given user. This option takes into account the time one spray iteration will take, so a pre-authentication delay may not occur every time  [default: 0]
  
  User options:
    -u, --user_file               File containing usernames to spray (one per line without domain)  [required]

  Password options: [mutually_exclusive, required]
    -p, --password                Password to spray
    -pf, --password_file          File containing passwords to spray (one per line)
    --passwords_in_userfile       Extract passwords from user_file (colon separated)

  Authentication options:
    -cID, --aad_client            Client ID used during authentication. Leave unspecified for random selection, or provide a comma-separated string
    -eID, --aad_endpoint          Endpoint ID used during authentication. Leave unspecified for random selection, or provide a comma-separated string

  User Agent options: [mutually_exclusive]
    -cUA, --custom_user_agent     Set custom user agent for authentication requests
    -rUA, --random_user_agent     Randomize user agent for authentication requests  [default: True]

  Shuffle options: [all_or_none]
    -S, --shuffle_auth_order      Shuffle order of authentication attempts so that each iteration (User1:Pass1, User2:Pass1, User3:Pass1) will be sprayed in a random order with a random arrangement of passwords, e.g (User4:Pass16, User13:Pass25, User19:Pass40). Be aware this option introduces the possibility that the time between consecutive authentication attempts for a given user may occur DELAY seconds apart. Consider using the-mD/--min_loop_delay option to enforce a minimum delay between authentication attempts for any given user.
    -SO, --shuffle_optimization_attempts [default: 10]

  -h, --help                      Show this message and exit.
```
</details>

<details>
  <summary>Generate Mode (Audit)</summary>
  
  ```
Usage: spray365.py generate audit [OPTIONS]

  Generate an execution plan to identify flaws in MFA / Conditional Access Policies. This works best with with known credentials.

Options:
  -ep, --execution_plan           File path where execution plan should be saved  [required]
  -d, --domain                    Office 365 domain to authenticate against  [required]
  --delay                         Delay in seconds to wait between authentication attempts  [default: 30]
  -mD, --min_loop_delay           Minimum time to wait between authentication attempts for a given user. This option takes into account the time one spray iteration will take, so a pre-authentication delay may not occur every time  [default: 0]

  User options:
    -u, --user_file               File containing usernames to spray (one per line without domain)  [required]

  Password options: [mutually_exclusive, required]
    -p, --password                Password to spray
    -pf, --password_file          File containing passwords to spray (one per line)
    --passwords_in_userfile       Extract passwords from user_file (colon separated)

  Shuffle options: [all_or_none]
    -S, --shuffle_auth_order      Shuffle order of authentication attempts so that each iteration (User1:Pass1, User2:Pass1, User3:Pass1) will be sprayed in a random order with a random arrangement of passwords, e.g (User4:Pass16, User13:Pass25, User19:Pass40). Be aware this option introduces the possibility that the time between consecutive authentication attempts for a given user may occur DELAY seconds apart. Consider using the-mD/--min_loop_delay option to enforce a minimum delay between authentication attempts for any given user.
    -SO, --shuffle_optimization_attempts [default: 10]

  -h, --help                      Show this message and exit.
```
</details>

<details>
  <summary>Spray Mode</summary>
  
  ```
Usage: spray365.py spray [OPTIONS]

  Password spray user accounts using an existing execution plan

Options:
  -ep, --execution_plan         File path to execution plan  [required]
  -l, --lockout                 Number of account lockouts to observe before aborting spraying session (disable with 0)  [default: 5]
  -R, --resume_index            Resume spraying passwords from this position in the execution plan  [x>=1]
  -i, --ignore_success          Ignore successful authentication attempts for users and continue to spray credentials. Setting this flag will enable spraying credentials for users even if Spray365 has already identified valid credentials.

  Proxy options: [all_or_none]
    -x, --proxy                 HTTP Proxy URL (format: http[s]://proxy.address:port)
    -k, --insecure              Disable HTTPS certificate verification

  -h, --help                    Show this message and exit.
```
</details>

<details>
  <summary>Review Mode</summary>
  
  ```
Usage: spray365.py review [OPTIONS] RESULTS

  View data from password spraying results to identify valid accounts and more

Options:
  --show_invalid_creds
  --show_invalid_users

  -h, --help            Show this message and exit.
```
</details>

## Acknowledgements
| Author | Tool / Other | Link |
| --- | --- | --- |
| [@__TexasRanger](https://twitter.com/__TexasRanger) | msspray: Conduct password spray attacks against Azure AD as well as validate the implementation of MFA on Azure and Office 365 endpoints | [https://github.com/SecurityRiskAdvisors/msspray](https://github.com/SecurityRiskAdvisors/msspray)

## Disclaimer
Usage of this software for attacking targets without prior mutual consent is illegal. It is the end user’s responsibility to obey all applicable local, state and federal laws, in addition to any applicable acceptable use policies. Using this software releases the author(s) of any responsiblity for misuse or damage caused.
