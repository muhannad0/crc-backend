# Website Visit Counter Backend

## Introduction
This is a simple website visit counter backend built using Python3. It's configured to run on AWS Lambda, using API Gateway to provide an API endpoint and DynamoDB to store counter data.

The whole stack can be deployed using the [Serverless Framework](https://www.serverless.com/).

## Requirements
+ Serverless Framework

    You can follow this guide for installation, [Serverless Framework: Getting Started](https://www.serverless.com/framework/docs/getting-started/).

+ Python 3
+ DynamoDB local installation

    I recommend using a Docker image to run DynamoDB for local development. You can find instructions to set it up on [Docker Hub](https://hub.docker.com/r/amazon/dynamodb-local/).

+ AWS credentials configured

## Deploying to AWS
+ In order to deploy this stack use:
```
serverless deploy --stage prod
```
*Note: If `--stage` variable is not provided a `dev` stage will be deployed by default.*

## Usage
+ The app has 2 API endpoints:
    + **GET Method**
        
        `https://<api-endpoint>/visit/{website}`
        
        For example:
        
        `https://<api-endpoint>/visit/example.com`
        
        Would return:
        ```
        {
            "code": "Success",
            "data": {
                "last_updated": 1591695923,
                "counter": 2,
                "site": "example.com"
            }
        }
        ```

    + **POST Method**
        
        `https://<api-endpoint>/visit`

        Use the following JSON body syntax:
        
        ```
        { "website": "example.com" }
        ```

        Would return:
        ```
        {
            "code": "Success",
            "data": {
                "last_updated": 1591733636,
                "counter": 3
            }
        }
        ```

## Python Code and Testing
The Python code for the Lambda can be run locally and tested using `unittest`.

To work on the Python code:
+ Create a Python virtual environmnet.
```
cd py-lambdafunc/

# create the environment
python3 -m venv env

# activate the environment
source env/bin/activate

# install the packages
(env) pip -r requirements.txt

# deactivate the environment once done
(env) deactivate
```


To run tests:
+ Start a local DynamoDB instance using Docker.
```
docker container run --rm -d -p 8000:8000 --name dynamodblocal amazon/dynamodb-local
```

+ Activate the environment.
```
cd py-lambdafunc/
source env/bin/activate
(env)
```
+ Run the tests.
```
(env) python -m unittest tests.py
...
(env)
----------------------------------------------------------------------
Ran 9 tests in 1.193s

OK
```

## References
I wrote about how I attempted to build this on my [blog](#).