
import os

import math

import time
import string
import boto3
from pika import spec
""" :type : pyboto3.s3 """
import random
from dotenv import dotenv_values


instanceMessageDeduplicationId = 0

config = dotenv_values("creds.env")

## remote
#config = dotenv_values("aws/creds.env")
region = config['region']


session = boto3.Session(
    aws_access_key_id=config['aws_access_key_id'],
    aws_secret_access_key=config['aws_secret_access_key'],
    aws_session_token= config['aws_session_token']
)

## NOTE: Alphabet characters are 97 (a) - 122 (z)
# vowels are (96 +): 1,5,9,15,21
vowel_numbers = [97, 101, 105, 111, 117] 
# consonant numbers:
consonant_list = list(range(97,123)) # start with full alphabet
for count2 in vowel_numbers: # remove vowels from alphabet 
    consonant_list.remove(count2) # list of consonants

# Useful parameters: 
NUM_NAMES = 9999 # number of names to generate
mx_name_blocks = 5 # max number of blocks that can be used  
vbl = 3 # max length of a single vowel block
cbl = 2 # max length of a single consonant block

def AddToDb(name = "defaultDb",  designation = 0, species = "unknownRace", desirable = 'no'):
    dbClient = session.resource('dynamodb', region_name=region)
    table = dbClient.Table(name)
    response = table.put_item(
    Item={
            'designation': designation,
            'info': {
                'species': species,
                'desirable': desirable
            }
        }
    )
    return response

def GetSpecies(tableName, designation):
    dbClient = session.resource('dynamodb', region_name=region)
    table = dbClient.Table(tableName)
    response = ""
    try:
        response = table.get_item(Key={'designation': designation})
    except:
        print("error")
    else:
        return response['Item']
    
def divide_chunks(l, n):
      
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

# launch and populate database with info if required
def LaunchDynamoDb(name = "defaultDb"):
    print("launching db  " + name)
    #dbClient = boto3.client('dynamodb', region = region)
    passed = False
    dbClient = session.resource('dynamodb', region_name=region)
    try:
        table = dbClient.create_table(
            TableName=name,
            KeySchema=[
                {
                    'AttributeName': 'designation',
                    'KeyType': 'HASH'  # Partition key
                }

            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'designation',
                    'AttributeType': 'N'
                }

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 100,
                'WriteCapacityUnits': 100
            }
        )
        print("launched db " + name)
        passed = True
        

    except:
        print("table already up")

    if(passed):
        print("Adding data to db, hold on")
        time.sleep(5)
        nameList = []
        # generate species list
        if os.path.exists("speciesList.txt"):
            os.remove("speciesList.txt")
        else:
            print("The file does not exist")

        f = open("speciesList.txt", "a")
        for i in range (0,NUM_NAMES):
            speciesName = GenerateAlienName()
            desirable =  random.choice(['yes', 'no'])
            record = str(i) + "," + speciesName + "," + desirable
            nameList.append(record)
        time.sleep(1)
        f.write("\n".join(nameList))
        f.close()

        
        chunks = list(divide_chunks(nameList, 25))
        for chunk in chunks:
            with table.batch_writer() as writer:
                for line in chunk:
                    print("write")
                    # print(str(line))
                    elements = line.split(',')
                    print(str(elements))
                    writer.put_item(Item={
                        'designation': int(elements[0]),
                        'info': {
                            'species': elements[1],
                            'desirable': elements[2]
                        }
                    }
        )
 


def GenerateAlienName():
    # Random number of blocks to use:
    n_vcs = random.randint(2,mx_name_blocks)

    # Randomly start vowel or consonant:
    vc_start = int(round(random.random(),0)) # v = 0, c = 1

    # Work out number of vowel or consonant blocks: 
    n_v = math.ceil(n_vcs/2) - vc_start*(n_vcs%2) # no. vowels
    n_c = n_vcs-n_v # no. consonants

    ### Generate vowel block list:

    vowel_block_list = list() # store all vowel blocks

    for count0 in range(1,1+n_v): # loop for each block

        vlength = random.randint(1,vbl) # random length of vowel block

        ### Generate single vowel blocks:

        v_block = list() # Store single vowel block

        for count1 in range(1,1+vlength): # loop for each individual vowel
            v1_val = chr(vowel_numbers[random.randint(0,4)]) # random vowel
            v_block.append(v1_val) # create list of vowels in single block


        string_block = ''.join(v_block) # join to make string

        vowel_block_list.append(string_block) # create list of all vowel blocks


    ### Generate consonant block list:

    const_block_list = list() # store all consonant blocks

    for count3 in range(1,1+n_c):
        clength = random.randint(1,cbl) # random length of block

        ### Generate single blocks:

        c_block = list() # store single block 

        for count4 in range(1,1+clength):
            c1_val = chr(consonant_list[random.randint(0,20)]) # random character
            c_block.append(c1_val)

        cstring_block = ''.join(c_block) 

        const_block_list.append(cstring_block) # list of consonant blocks


    ### Combine vowel and consonant blocks, alternating: 

    if n_v > n_c:
        mixed = []
        for i in range(len(vowel_block_list)):
             mixed.append(vowel_block_list[i])
             if i < len(const_block_list):
                mixed.append(const_block_list[i])
    else: 
        mixed = []
        for i in range(len(const_block_list)):
             mixed.append(const_block_list[i])
             if i < len(vowel_block_list):
                mixed.append(vowel_block_list[i])

    aName = ''.join(mixed).title()
    return aName
    



LaunchDynamoDb(name = "species_db")
species = GetSpecies("species_db", 478)
print(str(species))
info = species['info']
desirable = info['desirable']
speciesName = info['species']
print("desirable: " + str(desirable))
print("speciesName: " + str(speciesName))
print("designation: " + str(species['designation']))