#!/usr/bin/env python3
import os
import subprocess
import sys
import time

import boto3


# The main menu of the program. Prints all the available selections to choose from
def main():
    print("Please Choose one of the following")
    print("1. Create an Instance")
    print("2. List Instances")
    print("3. Terminate an Instance")
    print("4. Create a bucket")
    print("5. List Buckets")
    print("6. Delete a Bucket")
    print("7. Insert file or image in bucket")
    print("8. SSH into an instance")
    print("9. SCP check nginx file and index.html into instance (run after starting instance)")
    print("0. Exit")


# Refrences code given to us in the labs from Richard
# Uses user input to ssh into a specified instance and checks for errors
def sshscript():
    try:
        print("Please enter the IP address of the desired instance")
        ipadd = input()
        os.system("sudo ssh -t -i Key.pem ec2-user@" + ipadd)
        print("Success!")

    except subprocess.CalledProcessError:
        print("SSH failed, please try again")


# References code given to us in the labs from Richard
# runs a command to check if the nginx server is running
def checknginx():
    try:
        cmd = 'ps -A | grep nginx'

        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Nginx Server IS running")

    except subprocess.CalledProcessError:
        print("Nginx Server IS NOT running")


# References code given to us in the labs from Richard
# Creates instance using the key and adds it to a specified Security Group.
# Then updates and installs Python3, linux extras, nginx and starts nginx
# Then it creates a testfile to show it has successfully created and updated the instance
def createinstance():
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-0c21ae4a3bd190229',
        KeyName='Key',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=['sg-03f820e818a796a0f'],
        UserData='''#!/bin/bash
                    yum update -y
                    yum install python3 -y
                    amazon-linux-extras install nginx1.12 -y
                    service nginx start
                    touch /home/ec2-user/testfile''',  # to check all ok
        InstanceType='t2.micro')

    print("An instance with ID", instance[0].id, "has been created.")
    time.sleep(5)
    instance[0].reload()
    print("Public IP address:", instance[0].public_ip_address)


# Script used to scp the check_webserver.py file into the specified instance by asking user for the IP of the instance
# Also copies the html file into the instance
def scpcommand():
    cwcmd = "sudo scp -o StrictHostKeyChecking=no -i Key.pem check_webserver.py ec2-user@"
    direct = ":/home/ec2-user/"
    indexcmd = "sudo scp -i Key.pem index.html ec2-user@"
    print("Please enter the IP address of the desired instance")
    ipadd = input()
    try:
        subprocess.run(cwcmd + ipadd + direct, check=True, shell=True)
        time.sleep(10)
        print("check_webserver.py Copy successful")
        subprocess.run(indexcmd + ipadd + direct, check=True, shell=True)
        print("index.html Copy successful")
        # The index.html must be moved manually after ssh'ing into the instance.
        # I was unable to have it moved automatically through the command line
        print("Please remember to overwrite the old index.html file by running: ")
        print("'sudo mv index.html ../../usr/share/nginx/html'")
    except subprocess.CalledProcessError:
        print("Error running scp, please try again.")


# References code given to us in the labs from Richard

# Terminates a specified instance after asking user for the ID of the instance
def terminateinstance():
    ec2 = boto3.resource('ec2')
    print("Please enter your instance ID: ")
    instance_id = input()
    instance = ec2.Instance(instance_id)
    try:
        response = instance.terminate()
        print(response)
    except Exception as error:
        print(error)
        main()


# References code given to us in the labs from Richard
# Lists all instances
def listinstances():
    ec2 = boto3.resource('ec2')
    for instance in ec2.instances.all():
        print(instance.id, instance.state)


# References code given to us in the labs from Richard
# Creates a bucket in S3 and asks for the bucket name
def createbucket():
    s3 = boto3.resource("s3")
    print("Please enter your bucket name: ")
    bucket_name = input()
    try:
        response = s3.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}, ACL="public-read")
        print(response)
    except Exception as error:
        print(error + "please try again")
        main()


# References code given to us in the labs from Richard
# Lists all the buckets in the user's S3
def listbucket():
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)
        print("---")
    try:
        for item in bucket.objects.all():
            print("\t%s" % item.key)
    except Exception as error:
        print(error)


# References code given to us in the labs from Richard
# Asks for users bucket name, then asks for the file name to copy and sends it to the bucket
# Attempted to open the file browser, but haven't completed that yet
def putbucket():
    s3 = boto3.resource("s3")
    print("Please enter your bucket name: ")
    bucket_name = input()
    # webbrowser.open("/your/file/Path")
    print("Please enter the file/image name: ")
    object_name = input()
    try:
        response = s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'), ACL="public-read")
        print(response)
    except Exception as error:
        print(error)


# References code given to us in the labs from Richard
# Deletes the specified bucket
def deletebucket():
    s3 = boto3.resource('s3')
    print("Please enter your bucket name: ")
    bucket_name = input()
    bucket = s3.Bucket(bucket_name)
    try:
        response = bucket.delete()
        print(response)
    except Exception as error:
        print(error)


loop = True

# While Loop that acts as the menu selection. Each selection calls a different method
while loop:
    main()
    choice = input("Please enter your choice: ")
    if choice == "1":
        print(">> Creating Instance, please stand by.. ")
        createinstance()
        print("Press any key to continue.. ")
        input()
    elif choice == "2":
        print(">> List of all instances: ")
        listinstances()
        print("Press any key to continue.. ")
        input()
    elif choice == "3":
        print(">> Deleting specified instance.. ")
        terminateinstance()
        print("Press any key to continue.. ")
        input()
    elif choice == "4":
        print(">> Creating bucket, please stand by.. ")
        createbucket()
        print("Press any key to continue.. ")
        input()
    elif choice == "5":
        print(">> List of all buckets: ")
        listbucket()
        print("Press any key to continue.. ")
        input()
    elif choice == "6":
        print(">> Deleting specified bucket.. ")
        deletebucket()
        print("Press any key to continue.. ")
        input()
    elif choice == "7":
        print(">> Please specify bucket and file/image: ")
        putbucket()
        input()
    elif choice == "8":
        print(">> Running SSH script.. ")
        sshscript()
        print("Press any key to continue.. ")
        input()
    elif choice == "9":
        print(">> Copying check_webserver.py to instance.. ")
        scpcommand()
        print("Press any key to continue.. ")
        input()
    elif choice == "0":
        print(">> Exiting.. ")
        exit()
    else:
        print("I don't understand your choice.")

if __name__ == '__main__':
    main()

