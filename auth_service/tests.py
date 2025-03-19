from django.test import TestCase

# Create your tests here.
import smtplib

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("ettiolayinka4@gmail.com", "iorm etek wfrd yadp")
print("SMTP connection successful!")
server.quit()