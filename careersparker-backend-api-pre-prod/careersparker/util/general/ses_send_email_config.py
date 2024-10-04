import boto3
from botocore.exceptions import ClientError

from careersparker.settings import AWS_SES_REGION_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DEFAULT_FROM


def send_email(recipient=None, subject=None, body_html=None, sender=DEFAULT_FROM):
    """
    Sends an email using Amazon SES.

    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body_html (str): The HTML body of the email.
        sender (str): The email address of the sender.

    Returns:
        bool: True if the email was successfully sent, False otherwise.

    """

    if not recipient:
        recipient = 'drmayor2004@yahoo.com'  # in sandbox mode, this address must be verified

    if not subject:
        subject = "Amazon SES Test (SDK for Python)"

    if not body_html:
        body_html = """
        <html>
        <head></head>
        <body>
        <h1>Amazon SES Test (SDK for Python)</h1>
        <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
        AWS SDK for Python (Boto)</a>.</p>
        </body>
        </html>
        """

    CHARSET = "UTF-8"

    client = boto3.client(
        'ses',
        region_name=AWS_SES_REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # send email
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID: " + response['MessageId'])
        return True
