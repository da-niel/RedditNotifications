# Much of the code framework was taken from https://realpython.com/python-send-email/

import praw
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config
import time
from datetime import datetime, timezone, timedelta

USERNAME = config("REDDIT_USERNAME")
PASSWORD = config("REDDIT_PASSWORD")
CLIENT_ID = config("REDDIT_CLIENTID")
CLIENT_SECRET = config("REDDIT_CLIENTSECRET")
SENDER_EMAIL = config("SENDER_EMAIL")
SENDER_PASSWORD = config("SENDER_PASSWORD")
RECEIVER_EMAIL = config("RECEIVER_EMAIL")
COUNTRY = 'US'

subreddit = "mechmarket" # subreddit
wants = ['savage', 'ursa'] # key words
interestedPosts = []
email = ""
# collection of ids of posts already sent
read_posts = [] 

# get latest posts
def get_posts(num_posts = 100):
    for post in reddit.subreddit(subreddit).new(limit = num_posts):
        if post.id not in read_posts:
            # mark post as read
            read_posts.append(post.id)
            # if it's in the US
            if COUNTRY in post.title[:post.title.find('[H]')]:
                selling = post.title[post.title.find('[H]')+3:post.title.find('[W]')].strip(' ').lower()
                # if the user is selling something i'm interested in
                if any([True for want in wants if want in selling]):
                    # prep email
                    interestedPosts.append(f"<a href=\"{post.url}\">{post.title}, with {post.num_comments} comments</a> <br>")  

# parse email and send
def send_email():
    for post in interestedPosts:
        email = email + post
    email_list = [RECEIVER_EMAIL]
    subject = 'rMM Notification!'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    context = ssl.create_default_context()
    server.ehlo()
    server.starttls(context=context)
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    for email_address in email_list:
        # Send emails in multiple part messages
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = email_address
        # HTML of email content
        html = '''\
        <html>
            <head></head>
            <body>
            <p>
                <b style='font-size:20px'>Hello!</b><br><br>
                Look here:<br>
            </p>
            %s
            </body>
        </html>
        ''' % email
        msg.attach(MIMEText(html, 'html'))
        print("Sending Email...")
        server.sendmail(SENDER_EMAIL, email_address, msg.as_string())
        print("Email sent...")
    server.quit()

if __name__ == '__main__':

    reddit = praw.Reddit(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        user_agent = "reddit script",
        username = USERNAME,
        password = PASSWORD
    )

    while True:
        now = datetime.now(timezone.utc) - timedelta(hours = 7)
        num_posts = 10
        # get posts
        get_posts(num_posts)
        print(f"| {datetime.now()} | Posts Found: {len(interestedPosts)}")
        if len(interestedPosts) > 0:
            send_email()
            interestedPosts = []
        time.sleep(600)