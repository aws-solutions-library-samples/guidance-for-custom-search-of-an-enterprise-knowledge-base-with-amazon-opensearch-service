# get image and video from s3

### 1.depoy cloudfront for s3
Run the script:
```
https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=cloudfrontfors3&templateURL=https://s3-eu-west-1.amazonaws.com/tomash-public/AWS/s3bucket_with_cloudfront.yml
```

### 2.copy the image and video to the s3 bucket

Bucket name: cf-simple-s3-origin-cloudfrontfors32-xxxxxx



### 3.get in the image and video from cloudfront 

Find the cloudfront Domain name in the cloudfront, the description is 'A simple distribution with an S3 origin' 

The image or video url is: cloudfront domain name + video name, just as :video_url = 'https://xxxxxxxxx.cloudfront.net/' + video_name