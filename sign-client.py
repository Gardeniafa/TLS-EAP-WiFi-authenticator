#!/usr/bin/python3
import os
import sys
import subprocess
import random
import string

# define default values
default_options_values = {
    'C': 'US',
    'ST': 'CA',
    'L': 'San Francisco',
    'O': 'Gov',
    'OU': 'FBI',
}


def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + "_."
    return ''.join(random.choice(characters) for _ in range(length))

def execute_openssl_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e.stderr)
        sys.exit(1)

def generate_certificate(username, options, legacy=False, passwd=None, cak_path=None, cac_path=None, klen=None, vaild_days=None):
    default_options_values['CN'] = username
    options_values = {**default_options_values}
    # Update with user options
    for option in options:
        option_key, option_value = option.split("=")
        options_values[option_key.upper()] = option_value

    # Generate random password if not provided
    password = passwd or generate_random_password()

    # Define file names
    key_file = f"{username}.key"
    csr_file = f"{username}.csr"
    crt_file = f"{username}.crt"
    p12_file = f"{username}-legacy.p12" if legacy else f"{username}.p12"
    cak_path = cak_path or "/etc/freeradius/3.0/certs/ca.key"
    cac_path = cac_path or "/etc/freeradius/3.0/certs/ca.pem"
    klen = klen or "2048"
    vaild_days = vaild_days or "365"

    # check the type of klen and vaild_days
    try:
        int(vaild_days.strip())
    except ValueError:
        print("Error: Invalid valid days value, must be an integer.")
        sys.exit(1)

    try:
        int(klen.strip())
    except ValueError:
        print("Error: Invalid key length value, must be an integer.")
        sys.exit(1)

    # Check CA key and certificate files exist
    if not os.path.isfile(cak_path):
        print(f"CA key file not found: {cak_path}")
        sys.exit(1)
    if not os.path.isfile(cac_path):
        print(f"CA certificate file not found: {cac_path}")
        sys.exit(1)

    # check klen is valid
    try:
        klen = int(klen)
        if klen not in [1024, 2048, 4096]:
            print("Error: Key length must be one of 1024, 2048, or 4096.")
            sys.exit(1)
    except ValueError:
        print("Error: Invalid key length value.")
        sys.exit(1)

    # Generate RSA key
    print("Generating RSA key...")
    execute_openssl_command(f"openssl genrsa -out {key_file} {klen}")

    # Generate CSR
    # csr_command = f"openssl req -new -key {key_file} -out {csr_file} -subj \"/C={default_values['C']}/ST={default_values['ST']}/L={default_values['L']}/O={default_values['O']}/OU={default_values['OU']}/CN={default_values['CN']}\""
    csr_command = f"openssl req -new -key {key_file} -out {csr_file} -subj \"/C={options_values['C']}/ST={options_values['ST']}/L={options_values['L']}/O={options_values['O']}/OU={options_values['OU']}/CN={options_values['CN']}\""
    print("Generating CSR...")
    execute_openssl_command(csr_command)

    # Sign certificate
    print("Signing certificate...")
    execute_openssl_command(
        f"openssl x509 -req -in {csr_file} -CA {cac_path} -CAkey {cak_path} -CAcreateserial -out {crt_file} -days {vaild_days} -sha256"
    )

    # Export to P12 with optional legacy mode
    export_command = f"openssl pkcs12 {'-legacy' if legacy else ''} -export -out {p12_file} -inkey {key_file} -in {crt_file} -certfile {cac_path} -name \"{username} WiFi certificate\" -password pass:{password}"
    print("Exporting to PKCS12 format...")
    execute_openssl_command(export_command)

    print(f"Certificate generated successfully for {username}")
    print(f"PKCS12 password: {password}")
    print(f"All files are saved in the current directory: {os.getcwd()}")

def parse_arguments():
    args = sys.argv[1:]
    username = None
    options = []
    legacy = False
    passwd = None
    cak_path = None
    cac_path = None
    key_length = None
    vaild_days = None

    if '-help' in args or not args:
        print_help()
        sys.exit(0)

    readed_as_value = False
    for i, arg in enumerate(args):
        if readed_as_value:
            readed_as_value = False
            continue
        if '=' in arg:
            options.append(arg)
        elif arg == '-legacy':
            legacy = True
        elif arg == '-passwd':
            passwd = args[i + 1] if i + 1 < len(args) else None
            readed_as_value = True
        elif arg == '-cak':
            cak_path = args[i + 1] if i + 1 < len(args) else None
            readed_as_value = True
        elif arg == '-cac':
            cac_path = args[i + 1] if i + 1 < len(args) else None
            readed_as_value = True
        elif arg == '-vdays':
            vaild_days = args[i + 1] if i + 1 < len(args) else None
            readed_as_value = True
        elif arg == '-klen':
            readed_as_value = True
            key_length = args[i + 1] if i + 1 < len(args) else None
        elif username is None:
            username = arg

    if not username:
        print("Error: Username is required.")
        print_help()
        sys.exit(1)
    
    if not passwd:
        passwd = generate_random_password()

    return username, options, legacy, passwd, cak_path, cac_path, key_length, vaild_days

def print_help():
    help_text = """
    The TLS-EAP client certificate generation script.
    Usage:
      py3 script py <username> [-legacy] [-passwd <value>] [-klen <value>] [-vdays <value>] [-cak /path/to/ca/key] [-cac /path/to/ca/certificate] [options ...]
    Arguments:
      username        Specifies the username, which is used for naming related files, certificate CN, and name in the .p12 file.

    Options:
      options=value   Allows specifying certificate-related parameters such as C, ST, L, O, OU. Defaults to:
                      C=US, ST=SF, L=SF, O=CPUSA, OU=CPUSA
      -legacy         If specified, exports the .p12 file using -legacy mode. The filename will be <username>-legacy.p12. Some apple devices require this mode.
      -passwd value   If specified, sets the .p12 password to the provided value. If not specified, a random 10-character password is generated.
      -klen value     If specified, sets the length of the private key to the provided value, should in 1024, 2048 or 4096. Defaults to 2048.
      -vdays value    If specified, sets the validity period of the certificate to the provided value in days. Defaults to 365.
      -cak path       Specifies the path to the CA private key file. If not provided, defaults to /etc/freeradius/3.0/certs/ca.key.
      -cac path       Specifies the path to the CA certificate file. If not provided, defaults to /etc/freeradius/3.0/certs/ca.pem.
      -help           Displays this help message.

    Examples:
      python3 script.py username
      python3 script.py username -legacy
      python3 script.py -legacy username -vdays 180
      python3 script.py username c=US st=SF l=SF o=CPUSA ou=CPUSA -legacy -passwd 12121
      python3 script.py -passwd 12121 username -legacy -klen 2048 -cak /another/path/ca.key
      python3 script.py -legacy c=AU o=CPUSA st=WS l=WS ou=IT username -passwd 12345 -vdays 90 -cac /new/path/ca.pem -klen 4096
    """
    print(help_text)

if __name__ == "__main__":
    username, options, legacy, passwd, cak_path, cac_path, klen, vaild_days = parse_arguments()
    generate_certificate(username, options, legacy, passwd, cak_path, cac_path, klen, vaild_days)
