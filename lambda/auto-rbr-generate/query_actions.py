import boto3
import time
import os

glueDBName = os.environ['GlueDBName']
pXX = str(int(os.environ['pXX'])/100)
workGroupName = os.environ['workGroupName']

athena_client = boto3.client('athena')


def run_queries(queryList):
    for q in queryList.keys():
        transformedQuery = queryList[q]['Query'].replace("glueDBName",glueDBName).replace("pXX",pXX)
        r = athena_client.start_query_execution(
                                QueryString=transformedQuery,
                                WorkGroup=workGroupName
                            )
        queryList[q]['Id'] = r['QueryExecutionId']
    #print (queryList)
    print("Wait until all Athena Queries complete")
    pendingQueries = []
    for q in queryList.keys():
        pendingQueries.append(queryList[q]['Id'])
    while (pendingQueries != []):
        for q in queryList.keys():
            id = queryList[q]['Id']
            if id in pendingQueries:
                queryReturn = athena_client.get_query_execution(
                    QueryExecutionId=id)
                queryStatus = queryReturn['QueryExecution']['Status']['State']
                if queryStatus in ['FAILED','CANCELLED']:
                    print ("ERROR")
                    raise ("AthenaQueryReturnedError")
                elif queryStatus == 'SUCCEEDED':
                    #print (queryReturn)
                    pendingQueries.remove(id)
            time.sleep(1)
    return (queryList)