#!/usr/bin/env python3
import os
import subprocess
import sys
import time

import boto3


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
    print("9. SCP check nginx file into instance (run after starting instance)")
    print("0. Exit")


def sshscript():
    try:
        print("Please enter the IP address of the desired instance")
        ipadd = input()
        os.system("sudo ssh -i Key.pem ec2-user@" + ipadd)
        print("Success!")

    except subprocess.CalledProcessError:
        print("SSH failed, please try again")


def checknginx():
    try:
        cmd = 'ps -A | grep nginx'

        subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Nginx Server IS running")

    except subprocess.CalledProcessError:
        print("Nginx Server IS NOT running")


def createinstance():
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-0c21ae4a3bd190229',
        KeyName='MatKey2018',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=['sg-idnumber'],
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

def scpcommand():
    sshcmd = "sudo scp -o StrictHostKeyChecking=no -i Key.pem check_webserver.py ec2-user@"
    direct = ":/home/ec2-user/"
    print("Please enter the IP address of the desired instance")
    ipadd = input()
    try:
        subprocess.run(sshcmd + ipadd + direct, check=True, shell=True)
        print("Copy successful")
    except subprocess.CalledProcessError:
        print("Error running scp, please try again.")

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


def listinstances():
    ec2 = boto3.resource('ec2')
    for instance in ec2.instances.all():
        print(instance.id, instance.state)


def createbucket():
    s3 = boto3.resource("s3")
    print("Please enter your bucket name: ")
    bucket_name = input()
    try:
        response = s3.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        print(response)
    except Exception as error:
        print(error + "please try again")
        main()


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


def putbucket():
    s3 = boto3.resource("s3")
    print("Please enter your bucket name: ")
    bucket_name = input()
    # webbrowser.open("/your/file/Path")
    print("Please enter the file/image name: ")
    object_name = input()
    try:
        response = s3.Object(bucket_name, object_name).put(Body=open(object_name, 'rb'))
        print(response)
    except Exception as error:
        print(error)


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
