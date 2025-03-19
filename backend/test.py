import smtplib

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:  # Use SMTP_SSL
        smtp.login("ettiolayinka4@gmail.com", "ppbv nycl olky zhqu")  # Use your App Password
        print("SMTP connection successful!")
except Exception as e:
    print(f"SMTP connection failed: {e}")


# import smtplib

# try:
#     with smtplib.SMTP("smtp.gmail.com", 587) as smtp:  # Use 587 for STARTTLS
#         smtp.starttls()  # Upgrade to secure connection
#         smtp.login("ettiolayinka4@gmail.com", "ppbv nycl olky zhqu")  # Use App Password
#         print("SMTP connection successful!")
# except Exception as e:
#     print(f"SMTP connection failed: {e}")



# try:
#     with smtplib.SMTP("smtp.gmail.com", 587) as smtp:  # Use port 587
#         smtp.ehlo()  # Identify with the mail server
#         smtp.starttls()  # Upgrade connection to secure TLS
#         smtp.ehlo()  # Re-identify after STARTTLS
#         smtp.login("ettiolayinka4@gmail.com", "ppbv nycl olky zhqu")  # Use App Password
#         print("SMTP connection successful!")
# except Exception as e:
#     print(f"SMTP connection failed: {e}")
