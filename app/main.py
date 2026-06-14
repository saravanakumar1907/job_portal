from flask import Flask, render_template, request
import boto3
import uuid
import logging
 
app = Flask(__name__)
 
# Logging Configuration
logging.basicConfig(
    filename='/var/log/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
 
# AWS Clients
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')
sns = boto3.client('sns', region_name='ap-south-1')
 
# Replace these with your actual values
TABLE_NAME = 'Applications'
BUCKET_NAME = 'bucket-resume-s3'
TOPIC_ARN = 'arn:aws:sns:ap-south-1:509784656407:job-application-topic, arn:aws:sns:ap-south-1:784803613582:Job_application-topic'
 
 
@app.route('/', methods=['GET', 'POST'])
def apply():
 
    if request.method == 'POST':
 
        name = request.form['name']
        email = request.form['email']
        resume = request.files['resume']
 
        app.logger.info(f"Application submitted by {name} ({email})")
 
        app_id = str(uuid.uuid4())
 
        # Upload Resume to S3
        s3.upload_fileobj(
            resume,
            BUCKET_NAME,
            f"{app_id}-{resume.filename}"
        )
 
        app.logger.info(
            f"Resume uploaded to S3 for {name}"
        )
 
        # Store in DynamoDB
        table = dynamodb.Table(TABLE_NAME)
 
        table.put_item(
            Item={
                'application_id': app_id,
                'name': name,
                'email': email,
                'resume_key': f"{app_id}-{resume.filename}"
            }
        )
 
        app.logger.info(
            f"DynamoDB record created for {name}"
        )
 
        # Send SNS Notification
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='New Job Application',
            Message=f"New application from {name} ({email})"
        )
 
        app.logger.info(
            f"SNS notification sent for {name}"
        )
 
        return "Application submitted successfully!"
 
    return render_template('form.html')
 
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
