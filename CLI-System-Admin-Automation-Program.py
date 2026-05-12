#!/usr/bin/python3

#Aalok Dhonju

# importing all necessary modules
import os
import subprocess
import time
import logging
import argparse
import csv
import smtplib

# Setting up our basic logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', handlers=[
    logging.FileHandler("system_health.log"), # Logs written to file system_health.log
    logging.StreamHandler()
])

# Creating logger named error_log
error_logger = logging.getLogger("error_logger")
error_handler = logging.FileHandler("error_log.log")
error_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)

# Creating logger named my logger
logger = logging.getLogger("my_logger")

#creating console handler and file handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
file_handler = logging.FileHandler("system_health.log")
file_handler.setLevel(logging.DEBUG)

#adding console and file handler to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

#formatting file and console handler
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Function to create a single user
def create_user(args):
    logging.info(f"Creating user '{args.username}' with role '{args.role}'")
    try:
        # Linux command to add user
        os.system(f"sudo useradd -m {args.username}")
        logging.info(f"User '{args.username}' created successfully with home directory /home/{args.username}")
        if args.role == "admin":
            logging.info(f"Role '{args.role}' assigned with full access permissions.")
    except Exception as e:
        error_logger.error(f"Failed to create user '{args.username}': {str(e)}")

# Function created by Ethan and Liam
# Function to create a batch of users from a CSV file
def create_batch_users(args):
    csv_file = args.csv

    # Check if the CSV file exists
    if not os.path.exists(csv_file):
        error_logger.error(f"CSV file '{csv_file}' does not exist.")
        return

    logging.info(f"Creating users from CSV file: {csv_file}")
    try:
        with open(csv_file, newline='', mode='r') as file:
            csv_reader = csv.DictReader(file)

            # Ensure headers are split correctly
            csv_reader.fieldnames = [header.split()[0] for header in csv_reader.fieldnames]

            # Debugging: Print the headers to verify correctness
            logging.debug(f"CSV Headers: {csv_reader.fieldnames}")

            for row in csv_reader:
                # Ensure required fields are present
                if 'username' not in row or 'role' not in row or 'email' not in row:
                    error_logger.error(f"Missing 'username', 'role', or 'email' in row: {row}")
                    continue

                # Extraction for user details
                args.username = row['username'].split()[0]
                args.role = row['role'].split()[0]
                args.email = row['email'].split()[0]

                # Create the user
                create_user(args)

            # Send emails after user creation
            send_emails(csv_file)

        logging.info("Batch user creation completed successfully.")

    except Exception as e:
        error_logger.error(f"Failed to create users from batch: {str(e)}")


# Function to delete user
def delete_user(args):
    logging.info(f"Deleting user '{args.username}'")
    try:
        # Linux command to delete user using args.username
        os.system(f"sudo userdel -r {args.username}")
        logging.info(f"User '{args.username}' deleted successfully")
    except Exception as e:
        error_logger.error(f"Failed to delete user '{args.username}': {str(e)}")


# Function to update a user's password
def update_user(args):
    # Check if both username and password are provided
    if args.username and args.password:
        try:
            # Use subprocess to run the usermod command to update the user's password
            subprocess.run(['usermod', '-p', args.password, args.username], check=True)
            logging.info(f"Updating information for user '{args.username}'")
            logging.info(f"Password updated successfully for '{args.username}'.")
        except subprocess.CalledProcessError as e:
            error_logger.error(f"Failed to update password for user {args.username}: {e}")
    else:
        # Log an info message if no updates are specified or if required arguments are missing
        logging.info(f"No updates specified for user '{args.username}' or missing arguments.")

# Function created by Aalok, Ethan, Liam
# Function to send email notifications to user
def send_emails(csv_file):
    # Can be logged in if required the password is: Bhuntu@123
    sender = "bhuntu.dhonju@gmail.com"  # Test email
    pwd = "odef oogx rzkm tgfv"  # App-specific password for the sender
    smtp_server = "smtp.gmail.com"
    port = 587  # For STARTTLS

    try:
        with open(csv_file, newline='', mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                receiver = row['email'].split()[0]
                username = row['username'].split()[0]

                message = f"""
                Subject: Password Change Required

                Dear {username},

                This email is to notify you that your user account with the username: {username} has been created. Please change your password at your earliest convenience.

                Regards,
                System Administrator
                """

                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login(sender, pwd)
                    server.sendmail(sender, receiver, message)
                    logging.info(f"Email sent successfully to {receiver}")

    except Exception as e:
        error_logger.error(f"Failed to send emails: {str(e)}")

#organizes a directory by creating new directories for each extension
def organizeFiles(directory):
    if not os.path.isdir(directory):
        #testing if directory was inserted
        error_logger.error(f"Directory not found: {directory}")
        return
    extensionList = {}
    print("[INFO] program about to start")
    try:
        #searching through every file in directory
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            if os.path.isfile(path):
                prefix, extension = os.path.splitext(path)
                if extension[1] not in extensionList:
                    #creating new directories for each unique extension
                    dirNoPeriod = os.path.join(directory, f"{extension[1:]}_list")
                    extensionList[extension] = dirNoPeriod
                    if not os.path.exists(dirNoPeriod):
                        os.mkdir(dirNoPeriod)
                        print(f'[INFO] created new directory {dirNoPeriod}')
                #moving extentions to their extention folders
                newPath = os.path.join(extensionList[extension], file)
                os.rename(path, newPath)
                print(f"[INFO] moved {path} to {newPath}")
        print("[INFO] Organization complete")
    except Exception as es:
        #for any exceptions
        error_message = f"failed to organize files from {directory}. Error: {str(es)}"
        error_logger.error(error_message)
        print(f"[ERROR] {error_message}")

#function created by Ezra
#checks a file once for any mentions of the CRITICAL keyword
def monitorFileCritical(path):
    keyword = "CRITICAL"
    if not os.path.isfile(path):
        error_logger.error(f"File not found: {path}")
        return

    print(f"[INFO] monitoring {path} for critical messages")

    try:
        #searching a file for critical keyword
        with open(path, "r") as file:
            for line in file:
                if keyword in line:
                    cleanLine = line.strip()
                    logger.critical(f"critical message found: {cleanLine}")

    except Exception as es:
        error_message = f"failed to monitor files from {path}. Error: {str(es)}"
        error_logger.log(error_message)
        print(f"[ERROR] {error_message}")

#function created by Ezra
#checks if and when a file was monitored
def monitorFileAccess(path):
    if not os.path.isfile(path):
        #checking if input is a file
        error_logger.error(f"File not found: {path}")
        return

    logger.info(f"Monitoring file: {path}")
    try:
        lastModTime = os.stat(path).st_mtime
        while (True):
            time.sleep(60)

            if not os.path.isfile(path):
                #checking if file was deleted
                logger.info(f"File deleted: {path}")
                lastModTime = os.stat(path).st_mtime
                return
            currModTime = os.stat(path).st_mtime
            if lastModTime != currModTime:
                #comparing the last time the file has been modified to the current time
                logger.info(f"File modified: {path}")
                lastModTime = os.stat(path).st_mtime
            else:
                logger.info(f"No changes detected")

    except Exception as ex:
        error_logger.error(f"Failed to monitor file. Error: {str(ex)}")


# Function to get cpu usage using subprocess
def get_cpu_usage(args):
    # Making use of terminal command: top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}' | awk -F. '{print $1}
    # Reference site: https://askubuntu.com/questions/464226/how-to-get-cpu-usage-in-percentages
    # Try except block to handle errors graciously
    try:
        usage = subprocess.check_output(
            "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}' | awk '{print $1}'",
            shell=True,
            universal_newlines=True
        )
        return float(usage)
    # Catches error and logs it to error_log.log
    except Exception as err:
        error_logger.error(f"Failed to fetch CPU usage. Error: {err}")
        return None

# Function created by Aalok
# Function to get memory usage using subprocess
def get_memory_usage(args):
    # Making use of terminal command: free -m | grep 'Mem:' | awk '{printf (($2 - $3) / $2) * 100}'
    # Reference site: https://stackoverflow.com/questions/10585978/how-to-get-the-percentage-of-memory-free-with-a-linux-command
    # Try except block to handle errors graciously
    try:
        # $2 refers to second column, $3 refers to the third column of grep O/P which is total memory and used memory
        output = subprocess.check_output(
            "free -m | grep 'Mem:' | awk '{printf (($2 - $3) / $2) * 100}'",
            shell=True,
            universal_newlines=True
        )
        return float(output)
    # Catches error and logs it to error_log.log
    except Exception as err:
        error_logger.error(f"Failed fetching system memory usage. Error: {err}")
        return None


# Function to monitor system (cpu usage, memory usage) every 1 min for 10 mins
def monitor_system(args):
    # Default value for threshold 85 unless passed by user
    threshold = args.threshold
    logging.info("System health check every 1 minute for 10 minutes")
    for i in range(10):
        # Calls function get_cpu_usage & get_memory_usage
        cpu_usage = get_cpu_usage(args)
        memory_usage = get_memory_usage(args)
        # formats output to 2 decimal places
        log_message = f"CPU usage: {cpu_usage:.2f}%, Memory usage: {memory_usage:.2f}%"
        if cpu_usage is not None and cpu_usage > threshold:
            logging.warning(f"High CPU usage detected: {cpu_usage:.2f}%")
        if memory_usage is not None and memory_usage > threshold:
            logging.warning(f"High Memory usage detected: {memory_usage:.2f}%")
        logging.info(log_message)
        # Pauses program for 60 seconds
        time.sleep(60)
    # Logs the message to system_health.log
    logging.info("[INFO] Logged CPU and memory usage to system_health.log.")


# Function to check disk space using subprocess
def check_disk_space(args):
    # Making use of terminal command df -h /dir/
    # Default value for threshold 85 unless passed by user
    directory = args.dir
    threshold = args.threshold
    # Checks if directory has been specified
    if not directory:
        error_message = "The directory has not been specified for the disk space check. Use --dir to specify the directory."
        error_logger.error(error_message)
        print(f"[ERROR] {error_message}")
        return
    # Checks if the path exists using os path exists
    if not os.path.exists(directory):
        error_message = f"The directory '{directory}' does not exist please input valid directory"
        error_logger.error(error_message)
        print(f"[ERROR] {error_message}")
        return

    logging.info(f"Checking disk space for directory {directory}")
    # Try except block to handle errors graciously
    try:
        output = subprocess.check_output(["df", "-h", directory], universal_newlines=True)
        lines = output.split("\n")
        if len(lines) > 1:
            disk_info = lines[1].split()
            usage = int(disk_info[4].replace('%', ''))
            if usage > threshold:
                logging.warning(f"[ALERT] Disk usage at {usage}% - consider freeing up space.")
            else:
                logging.info(f"[INFO] Disk usage at {usage}%. All good!")
    # Catches error and logs it to error_log.log
    except Exception as err:
        error_message = f"Not able to check disk space for {directory}. Error: {str(err)}"
        error_logger.error(error_message)
        print(f"[ERROR] {error_message}")


# Function to list processes using subprocess
def list_processes(args):
    filter_name = args.filter
    # Try except block to handle errors graciously
    try:
        if filter_name:
            command = f"ps aux | grep {filter_name}"
        else:
            command = "ps aux"
        command_output = subprocess.check_output(command, shell=True, universal_newlines=True)
        if command_output:
            logging.info(f"Processes found:")
            print(command_output)
        else:
            logging.info("No processes found.")
    # Catches error and logs it to error_log.log
    except Exception as err:
        error_message = f"Failed to list processes. Error: {err}"
        error_logger.error(error_message)
        print(f"[ERROR] {error_message}")

# Function that parses arguments from argparser
def parser():
    # Main parser
    main_parser = argparse.ArgumentParser(prog="System Admin Tool",
                                          description="Final Project Assignment: Comprehensive System Administration Project")
    subparsers = main_parser.add_subparsers(dest="command")

    # Function created by Ethan Liam
    # Monitor sub parser
    user_parser = subparsers.add_parser('user', help='User management operations',
                                        description='User houses the create/s and deletion')
    # Monitoring options
    user_parser.add_argument('--create', action='store_true', help='Create a single user')
    user_parser.add_argument('--create-batch', action='store_true', help='Create users from a CSV file')
    user_parser.add_argument('--delete', action='store_true', help='Delete a user')
    user_parser.add_argument('--username', help='Username for the user')
    user_parser.add_argument('--role', help='Role for the user (admin/user)')
    user_parser.add_argument('--email', help='Email for the user')
    user_parser.add_argument('--csv', help='Path to the CSV file')
    user_parser.add_argument('--update', action='store_true', help='Update user details (requires --username, --password)')
    user_parser.add_argument('--password', help='New password for the user')

# Function created by Aalok
    # Monitor sub parser
    monitor_parser = subparsers.add_parser("monitor", help="Monitors various system resources (system, disk, processes)",
                                           description="System Monitoring for managing system")
    # Monitoring options
    monitor_parser.add_argument("--system", action="store_true", help="Monitors system health (CPU and memory)")
    monitor_parser.add_argument("--disk", action="store_true", help="Checks disk space usage")
    monitor_parser.add_argument("--dir", type=str,  help="Directory to monitor for disk usage")
    # Default threshold value set as 85
    monitor_parser.add_argument("--threshold", type=int, default=85, help="Threshold so that alerts can be sent if it exceeds user parameter")
    monitor_parser.add_argument("--list_processes", action="store_true", help="Lists all the running processes")
    monitor_parser.add_argument("--filter", type=str, default=None, help="Filters processes by name from the list of running processes")

    #function created by Ezra Faith
    #organize subparser
    organize_parser = subparsers.add_parser("organize")

    #organize options
    organize_parser.add_argument('--dir', type=str, help='organize directory (type full path to directory)')
    organize_parser.add_argument('--log-monitor', type=str, help='monitor file for critical information (type full path to file)')
    organize_parser.add_argument('--access-monitor', type=str, help='monitor file for access information (type full path to file)')

    args = main_parser.parse_args()

    # Function created by Aalok
    if args.command == "monitor":
        if args.system:
            monitor_system(args) # Sends args to function monitor_system
        elif args.disk:
            if args.dir:
                check_disk_space(args) # Sends args to function check_disk_space
            else:
                # Prints error if --dir is not provided
                print("[ERROR] --dir required to use option --disk")
                print("[INFO] Please use -h for help. ")
        elif args.list_processes:
            list_processes(args) # Sends args to function list_processes
        else:
            print("[ERROR] Valid monitoring option's not provided. Please use -h for help.")

    # Function created by Ezra
    elif args.command == 'organize':
        if args.dir:
            organizeFiles(args.dir) # Sends args to function organizeFiles
        elif args.log_monitor:
            monitorFileCritical(args.log_monitor) # Sends args to function monitorFileCritical
        elif args.access_monitor:
            monitorFileAccess(args.access_monitor) # Sends args to function monitorFileAccess
        else:
            #prints error if code is incorrect
            parser.print_help()
            print("[INFO] Please use -h for help. ")

    # Function created by Ethan & Liam
    elif args.command == 'user':
        # Executes the create_user function for the creation of ONE user
        if args.create:
            if not args.username or not args.role:
                error_logger.error("--create requires --username and --role")
                return
            create_user(args)
        # Executes the create_batch_users function for the creation of multiple users from CSV file
        elif args.create_batch:
            if not args.csv:
                error_logger.error("--create-batch requires --csv")
                return
            create_batch_users(args)
        # Executes delete_user to delete a known username
        elif args.delete:
            if not args.username:
                error_logger.error("--delete requires --username")
                return
            delete_user(args)
        # Executes update_user to update a user's password
        elif args.update:
            if not args.username or not args.password:
                error_logger.error('Error --update requires --username and --password')
                return
            update_user(args)
        else:
            error_logger.error("No valid action provided under 'user'")

# Main Function
def main():
    # Try except block to handle errors graciously
    try:
        # Calls function parser to parse cli args
        parser()
    # Catches error and logs it to error_log.log
    except Exception as err:
        error_logger.error(f"Error occured: {err}")
        print("[INFO] Please use -h for help. ")
        print(f"[ERROR] Error occured: {err}")

if __name__ == "__main__":
    main()

