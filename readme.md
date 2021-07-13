This project leverages AWS to build a data pipeline from the reddit's API to S3.
The following AWS services will be required to easily deploy this:
- ECR
- ECS
- Fargate
- Kinesis Firehose
- S3

To emulate the ECS environment and run this locally using credentials in your ~/.aws folder:

```
docker-compose up
```
