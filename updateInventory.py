from ftplib import FTP_TLS

# Set up connection to FTP server
ftps = FTP_TLS()
ftps.connect('ftp.tapww.com', 22, timeout=120)
ftps.set_debuglevel(1)
ftps.set_pasv(True)
ftps.login('tapinv', 'T@p1NV0210!')
ftps.prot_p()

# Create local file to store contents of Inventory file
f = open('inv.txt', 'wb')

# Retrieve the Inventory file contents and store locally
ftps.retrbinary('RETR Inventory.txt', f.write)

# Close local file
f.close()

# Close the connection
ftps.quit()