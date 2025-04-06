import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('labjuno2022@gmail.com', 'yajj nqbp tqkt qwei')
server.sendmail('labjuno2022@gmail.com', 'labjuno2022@gmail.com', 'test')
server.quit()