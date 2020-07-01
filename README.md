# Website Visit Counter Backend

## Introduction
This is a simple website visit counter backend built using Python3. It's configured to run on AWS Lambda, using API Gateway to provide an API endpoint and DynamoDB to store counter data.

The whole stack can be deployed using the [Serverless Framework](https://www.serverless.com/).

## Requirements
+ Serverless Framework
    
    You can follow this guide for installation, [Serverless Framework: Getting Started](https://www.serverless.com/framework/docs/getting-started/).

+ Serverless Plugins:
    + [Serverless Offline](https://www.npmjs.com/package/serverless-offline)
    + [Serverless DynamoDB Local](https://www.npmjs.com/package/serverless-dynamodb-local)

+ Python 3
+ AWS credentials configured

## Development Setup
### Serverless Framework
+ Install the required packages.
```
npm install
```
+ Install Serverless DynamoDB Local.
```
sls dynamodb install
```

### Python Code
#### Developing the backend.
+ Create a Python virtual environment.
```
# create the environment
python3 -m venv env

# activate the environment
source env/bin/activate

# install the packages
(env) pip -r requirements.txt

# deactivate the environment once done
(env) deactivate
```


#### Unit Testing
Tests are run using `unittest`. [Moto](https://github.com/spulec/moto) is used to emulate AWS resources such as DynamoDB.

+ Activate the environment.
```
source env/bin/activate
(env)
```
+ Run the tests.
```
(env) python -m unittest discover tests/
...
(env)
----------------------------------------------------------------------
Ran 11 tests in 0.853s

OK
```

### Local Integration Testing
+ Start the local API server, Lambda runtime and DynamoDB instance.
```
sls offline start
```

You can make API calls to the local URLs using a tool such as [Postman](https://www.postman.com/).


## Deploying to AWS
+ In order to deploy this stack use:
```
serverless deploy --stage prod
```
*Note: If `--stage` variable is not provided a `dev` stage will be deployed by default.*

## API Reference
+ The app has 3 API endpoints:
    + **GET Method**
        
        `https://<api-endpoint>/site/{website}`
        
        Returns details of a single site.
        
        For example:
        
        `https://<api-endpoint>/site/example.com`
        
        Would return:
        ```
        {
            "last_updated": 1593625162,
            "site": "example.com",
            "counter": 1
        }
        ```

        `https://<api-endpoint>/sites/`

        Returns details of all saved sites.

        Would return:
        ```
        [
            {
                "last_updated": 1593625214,
                "site": "example.net",
                "counter": 1
            },
            {
                "last_updated": 1593625162,
                "site": "example.com",
                "counter": 1
            }
        ]

        ```

    + **POST Method**
        
        `https://<api-endpoint>/site`
        
        Saves site and returns details.

        Use the following JSON body syntax:
        
        ```
        { "website": "example.com" }
        ```

        Would return:
        ```
        {
            "last_updated": 1593625162,
            "site": "example.com",
            "counter": 1
        }
        ```

## References
I wrote about how I attempted to build this on my [blog](https://muhannad0.github.io/post/phase3-build-site-visit-counter-apigateway-lambda-dynamodb-cloudresumechallenge/).

*Note: The above post explains the first version of this app. However, this new version has been refactored to make the code more readable, enable faster and seamless local development and better test coverage.*