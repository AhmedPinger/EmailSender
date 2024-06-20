# EmailSender

### Improved Explanation

This Python script can be used to send emails using the `AWS SES` email service and is also integrated with `HubSpot Listings` to fetch emails directly from HubSpot lists by entering the `list ID`. The script asks for a series of details, and you can respond with `Yes` or `No`. In the end, it sends emails to the individuals whose addresses are in the specified `HubSpot list`.

Additionally, this script is not limited to just sending emails. It can also register users' emails to a `CTFd` server by generating random passwords and then providing all of the passwords at the end, as well as sending those credentials via email. Furthermore, there is an option to send OpenVPN packs. You can upload all VPN packs to an `AWS S3 Bucket` with filenames matching the email addresses (e.g., if the email is `ahmed@gmail.com`, the VPN pack should be named `ahmed.ovpn`). The code will automatically generate the complete URL (e.g., `https://s3.us-west-2.amazonaws.com/openvpn_files/ahmed.ovpn`). The part of the URL before `ahmed.ovpn` is hardcoded into the code, and the code appends the `ahmed.ovpn` to complete the URL if the VPN pack exists there. And at the end, and to keep all of the record, scripts just save all of the data to `CSV` file that can be seen later.

# The Questions that Script Asks

<img width="709" alt="image" src="https://github.com/AhmedPinger/EmailSender/assets/90968663/21de8c52-369d-4023-9a7e-690f4ab13a2b">

# Pre-Requisits

You should have your `Access` & `Secret Access` key stored in your `AWS Cli` Tool, and the script will automatically fetch the details from there.

# Code Modification

- At line number 15, you need to define the `AWS` region in which you have that Email.
- At line number 22, write down the email address you want to use to send Emails.
