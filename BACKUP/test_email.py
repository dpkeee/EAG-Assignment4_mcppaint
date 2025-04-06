import smtplib
import json

#@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email"""
    print("CALLED: send_email(to: str, subject: str, body: str) -> dict:")
    
    # Load email configuration from JSON file
    with open('config.json') as config_file:
        config = json.load(config_file)
    
    email = config['email']
    password = config['password']
    
    # Create the email headers
    message = f"Subject: {subject}\n\n{body}"  # Format the email with subject and body
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, to, message)  # Send the email with the formatted message
    server.quit()
    
    return "Email sent successfully"

# Call the function
send_email(to="labjuno2022@gmail.com", subject="Tested2 Email Subject", body="The2 is the body of the email.")
