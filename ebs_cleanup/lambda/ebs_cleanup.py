from datetime import datetime, timedelta, timezone
import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


IGNORE_WINDOW = 30


def handler(event, context):
    region = boto3.session.Session().region_name

    startDateTime = datetime.today() - timedelta(IGNORE_WINDOW)
    eventList = getCloudTrailEvents(startDateTime, region)
    logger.info("There are {} EC2:DetachVolume events".format(len(eventList)))
    activeVols = getRecentActiveVolumes(eventList)
    logger.info("There are {} recently detached volumes".format(len(activeVols)))
    availableVols = getAvailableVolumes(region)
    logger.info("There are {} detached volumes".format(len(availableVols)))
    flaggedVols = identifyAgedVolumes(availableVols, activeVols)

    if flaggedVols == None:
        # No unused volume found
        return

    logger.info("There are {} unused volumes".format(len(flaggedVols)))
    estimate_cost_savings(flaggedVols)

    ec2 = boto3.client("ec2")
    for vol in flaggedVols:
        response = ec2.delete_volume(VolumeId=vol)
        logger.info("Removing volume " + vol)


def getAvailableVolumes(rgn):
    # returns list of volumes in 'available' state
    ec2 = boto3.client('ec2', region_name=rgn)
    availableVolList = []
    filterList = [{'Name': 'status', 'Values': ['available']}]
    response = ec2.describe_volumes(Filters=filterList, MaxResults=500)
    for v in response['Volumes']:
        # Ignore volumes that are created within IGNORE_WINDOW
        if (datetime.now(timezone.utc) - v['CreateTime']).days > IGNORE_WINDOW:
            availableVolList.append(v['VolumeId'])
    while ('NextToken' in response):
        response = ec2.describe_volumes(Filters=filterList, MaxResults=500, NextToken=response['NextToken'])
        for v in response['Volumes']:
            availableVolList.append(v['VolumeId'])
    return availableVolList

def getRecentActiveVolumes(events):
    # parses volumes from list of events from CloudTrail
    recentActiveVolumeSet = set()
    for e in events:
        for i in e['Resources']:
            if i['ResourceType'] == 'AWS::EC2::Volume':
                recentActiveVolumeSet.add(i['ResourceName'])

    return recentActiveVolumeSet

def identifyAgedVolumes(availableVolList, activeVolSet):
    # remove and return EBS volumes which are recently active from the list of available volumes
    if len(availableVolList) == 0:
        return None
    else:
        agedVolumes = list(set(availableVolList) - activeVolSet)
        return agedVolumes

def estimate_cost_savings(oldVolList):
    total_size = 0
    ec2 = boto3.resource('ec2')

    for vol_id in oldVolList:
        vol = ec2.Volume(id=vol_id)
        total_size += vol.size

    logger.info("Total amount of storage to delete {}GB".format(total_size))
    logger.info("Total savings (if all GP2): $" + str(total_size * 0.119))

def getCloudTrailEvents(startDateTime, rgn):
    # gets CloudTrail events from startDateTime until "now"
    cloudTrail = boto3.client('cloudtrail', region_name=rgn)
    attrList = [{'AttributeKey': 'EventName', 'AttributeValue': 'DetachVolume'}]
    eventList = []
    response = cloudTrail.lookup_events(LookupAttributes=attrList, StartTime=startDateTime, MaxResults=50)
    eventList += response['Events']
    while ('NextToken' in response):
        response = cloudTrail.lookup_events(LookupAttributes=attrList, StartTime=startDateTime, MaxResults=50,
                                            NextToken=response['NextToken'])
        eventList += response['Events']
    return eventList
