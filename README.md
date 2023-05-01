TODO: Fix formatting 

# How to build a Python solution that integrates with Reddit API and ChatGPT API

First, you'll need to create a Reddit developer account and obtain an API key and secret, which will allow your Python code to access Reddit data. You can find more information on how to do this here: https://www.reddit.com/dev/api/

Next, you'll need to use a Python Reddit API wrapper such as PRAW (Python Reddit API Wrapper) to access the Reddit API from your Python code. You can install PRAW using pip:
pip install praw

Once you have PRAW installed, you can use it to search for relevant posts and comments on Reddit using a specific query. For example, to search for posts and comments related to "compute" on the "Azure" subreddit, you can use the following code: dtsocial-1.py

This will search the "Azure" subreddit for posts and comments containing the phrase "compute" and print out the title and text of each result.

Next, you can integrate this Reddit search functionality into your ChatGPT solution. You can use a ChatGPT API wrapper such as OpenAI's official Python package openai to send a question to the ChatGPT API and receive a response. Here's an example code snippet that combines both the Reddit search and ChatGPT API functionality: dtsocial-2.py

This code will prompt the user to enter a question, and then use the Reddit API to search for relevant posts and comments on the "Azure" subreddit, and use the ChatGPT API to generate a response to the user's question. The results will be printed to the console.

To take this one step further, build a front-end for the chatbot above, you can use a web development framework such as Flask or Django. Here's an example using Flask:

Install Flask and PRAW libraries using pip: pip install Flask praw

Create a new file called app.py and add the following code: app.py

Create two new HTML files called index.html and results.html

Start the Flask app by running python app.py in the terminal. The app will run on http://localhost:5000 by default.

Now you can visit http://localhost:5000 in your web browser and enter a question into the form. The app will display the Reddit search results and the response generated by the OpenAI API on the results page.

Note that this is a basic example and you may need to customize it to meet your specific needs. Additionally, be aware of any rate limiting or usage restrictions that may apply to the Reddit API and ChatGPT API.

## To deploy the code from the GitHub repository you provided to an Azure App Service, you can follow these general steps:

Go to the Azure portal (portal.azure.com) and sign in.
Create a new App Service by clicking the "+ Create a resource" button and searching for "App Service".
Follow the prompts to configure the App Service with a unique name, resource group, subscription, and other necessary settings.
Set up deployment credentials:

In the App Service, go to the "Deployment Center" section.
Choose the source control option as GitHub and authorize Azure to access your GitHub account.
Provide your GitHub credentials, if prompted.
Choose the repository and branch you want to deploy.
Configure the App Service:

In the App Service, go to the "Configuration" section.
Add the necessary environment variables such as Flask_APP (set this to the name of your app.py file), Flask_ENV (set this to "production"), and any other necessary environment variables for your application.
Add any necessary modules and packages required for your Flask application to run.
Deploy the code:

In the App Service, go to the "Deployment Center" section.
Choose the deployment source you just set up and click "Deploy".
Wait for the deployment to complete.
Once the deployment is complete, you should be able to access your Flask application at the URL of your Azure App Service.

**NOTE** If you plan on making your app publically accessible, you might want set a usage limit on your OpenAI account :)  

Are you considering using Azure OpenAI in an enterprise environment but concerned on the resource domain placement and how to secure the service? There are a many supporting services that could be utilised based on the business requirements, but I want to provide an example, which due to its simplicity and flexibility involves running Application Gateway and Azure Firewall in parallel. This is one of the emerging practices but there are many others that can be drawn upon here . These patterns can be leveraged as you are planning to secure you application workload in a highly available manner. This architecture addresses the needs of individuals and organizations seeking to additionally protect backend APIs from unauthorized users, as well as leveraging API Management features such as throttling, rate limiting, and IP filtering to prevent overloading of APIs.
Initially when deciding which architecture might be the best starting point, I would recommend the below workflow to assist in making that decision and adjust accordingly. 
 
This solution presented in this blog works best when there is a mix of web and non-web workloads in the virtual network (VNet), so we have chosen to go with Azure Application Gateway  (AppGW) with Azure Firewall in parallel. Azure WAF in AppGW protects inbound traffic to the web workloads, and the Azure Firewall inspects inbound traffic for the other applications. The Azure Firewall will cover outbound flows from both workload types. For web applications that only use HTTP(S), Azure Front Door is a better global load balancing solution than Traffic Manager. Front Door is a layer-7 load balancer that also provides caching, traffic acceleration, SSL/TLS termination, certificate management, health probes, and other capabilities.

## Workflow
Azure Traffic Manager uses DNS-based routing to load balance incoming traffic across the two regions. Traffic Manager resolves DNS queries for the application to the public IP addresses of the AppGW endpoints. The public endpoints of the AppGWs serve as the backend endpoints of Traffic Manager. Traffic Manager resolves DNS queries based on a choice of six routing methods. In this architecture, Traffic Manager would be configured to use performance routing. It routes traffic to the endpoint that has the lowest latency for the user. Traffic Manager automatically adjusts its load balancing algorithm as endpoint latency changes. Traffic manager provides automatic failover if there's a regional outage. It uses priority routing and regular health checks to determine where to route traffic. The browser connects directly to the endpoint. Traffic Manager doesn't see the HTTP(S) traffic as depicted in the diagram below. 

Inbound HTTP(S) connections from the Internet traverse Traffic Manager and should be sent to the public IP address of the Application Gateway, HTTP(S) connections from Azure or on-premises to its private IP address. Standard VNet routing will send the packets from the Application Gateway to the destination workload, as well as from the destination workload back to the Application Gateway (see the packet walk further down for more details). For inbound non-HTTP(S) connections, traffic should be targeting the public IP address of the Azure Firewall (if coming from the public Internet), or it will be sent through the Azure Firewall by User Defined Routes (UDR) (if coming from other Azure VNets or on-premises networks). All outbound flows from Azure VMs will be forwarded to the Azure Firewall by UDR.
The following table summarizes the traffic flows for this scenario:

Flow	Goes through Application Gateway / WAF	Goes through Azure Firewall
HTTP(S) traffic from internet/onprem to Azure	Yes	No
HTTP(S) traffic from Azure to internet/onprem	No	Yes
Non-HTTP(S) traffic from internet/onprem to Azure	No	Yes
Non-HTTP(S) traffic from Azure to internet/onprem	No	Yes

## Packet walkthrough
The request to the Application Gateway public IP is distributed to a back-end instance of the gateway, in this case an example IP address 192.168.200.7. The Application Gateway instance that receives the request stops the connection from the client, and establishes a new connection with one of the back ends. The back end sees the Application Gateway instance as the source IP address. The Application Gateway inserts an X-Forwarded-For HTTP header with the original client IP address.

1 Source IP address: 192.168.200.7 (the private IP address of the Application Gateway instance)
· Destination IP address: 192.168.1.4
· X-Forwarded-For header: ClientPIP

2. The VM answers the application request, reversing source and destination IP addresses. The VM already knows how to reach the Application Gateway, so doesn't need a UDR.
· Source IP address: 192.168.1.4
· Destination IP address: 192.168.200.7

3. Finally, the Application Gateway instance answers the client:
·  Source IP address: AppGwPIP
·  Destination IP address: ClientPIP

Azure Application Gateway adds metadata to the packet HTTP headers, such as the X-Forwarded-For header containing the original client's IP address. Some application servers need the source client IP address to serve geolocation-specific content, or for logging. For more information, see How an application gateway works. The flow is similar if the client comes from an on-premises network over a VPN or ExpressRoute gateway. The difference is the client accesses the private IP address of the Application Gateway instead of the public address. This design gives much more granular egress filtering than NSGs. For example, if applications need connectivity to a specific Azure Storage Account, you can use fully qualified domain name (FQDN)-based filters. With FQDN-based filters, applications aren't sending data to rogue storage accounts. That scenario couldn't be prevented just by using NSGs. This design is often used where outbound traffic requires FQDN-based filtering.

Whilst APIM provides the ability to white-list specific source IP addresses, the benefit of this architecture is that non-permitted API requests are blocked at the perimeter of your network.

## Components
•	Azure Virtual Network enables Azure resources to securely communicate with each other, the internet, and on-premises networks.

•	Azure Private Link enables you to access Azure PaaS Services (for example, Azure Storage and SQL Database) and Azure hosted customer-owned/partner services over a private endpoint in your virtual network.

•	Azure Private DNS allows domain names to be resolved in a virtual network without needing to add a custom DNS solution.

•	Azure API Management helps organizations publish APIs to external, partner, and internal developers to use their data and services.

•	Azure storage account contains all of your Azure Storage data objects, including blobs, file shares, queues, tables, and disks. 

•	Azure DDoS Protection Standard, combined with application-design best practices, provides enhanced DDoS mitigation features to provide more defense against DDoS attacks. You should enable Azure DDOS Protection Standard on any perimeter virtual network.

•	Azure Firewall is a managed next-generation firewall that offers network address translation (NAT). Azure Firewall bases packet filtering on Internet Protocol (IP) addresses and Transmission Control Protocol and User Datagram Protocol (TCP/UDP) ports, or on application-based HTTP(S) or SQL attributes. Azure Firewall also applies Microsoft threat intelligence to identify malicious IP addresses. For more information, see the Azure Firewall documentation.

•	Azure Firewall Premium includes all functionality of Azure Firewall Standard and other features, such as TLS-inspection and Intrusion Detection and Protection System (IDPS).

•	Azure Application Gateway is a managed web traffic load balancer and HTTP(S) full reverse proxy that can do Secure Socket Layer (SSL) encryption and decryption. Application gateway preserves the original client IP address in an X-Forwarded-For HTTP header. Application Gateway also uses Web Application Firewall to inspect web traffic and detect attacks at the HTTP layer. For more information, see the Application Gateway documentation.

•	Azure Web Application Firewall (WAF) is an optional addition to Azure Application Gateway. It provides inspection of HTTP requests, and it prevents malicious attacks at the web layer, such as SQL Injection or Cross-Site Scripting. 

•	Azure Key Vault enables users to securely store and manage cryptographic keys, secrets, and certificates used to authenticate and secure applications, services, and data in the cloud.

•	Azure Front Door enables users to optimize and secure web traffic by routing it to the closest available service endpoint based on real-time performance metrics and geo-proximity.

•	Azure OpenAI offers an integrated AI platform with pre-built models, tools, and services to enable developers and businesses to build and scale AI applications and solutions quickly and easily.


## Key takeaways
•	You cannot use the Key Vault service firewall to restrict network access at the time of publishing this blog with Azure Cognitive Services. Azure Cognitive Services is not considered a Trusted Azure Service for Key Vault and thus can’t be allowed network access when the service firewall is enabled. Azure Key Vault should be secured with Azure AD authentication and Azure RBAC vault policies for authorization.
•	The DNS namespace for the OpenAI service is privatelink.openai.azure.com. It is recommended the DNS namespace for the OpenAI service (privatelink.openai.azure.com) is hosted in Azure Private DNS.  
•	Azure OpenAI has a service Firewall like many other PaaS services. Customers can allow access from all networks, which is not something I would generally not recommend outside of a PoC. The recommended guidance is to restrict access to select networks and/or private endpoints. 
•	Azure OpenAI does not support the use of a managed identity for access to an Azure Storage. This means you’ll need to secure the data using a SAS tokens which means you cannot take advantage of service instance authorization rules. 

Microsoft Defender for Cloud, Azure Monitor and Azure Policy are all fundamentals and should already be in place within your Azure eco-system, therefore they are not explicitly called out in this blog. If you are not using these foundational services and are looking for assistance, please reach out to your account team.  

## Sample architecture
![image](https://user-images.githubusercontent.com/107463700/235384241-868923d9-5f0a-4709-abd0-469a926f5b3a.png)

## DISCLAIMER
The sample scripts are not supported under any Microsoft standard support program or service. The sample scripts are provided AS IS without warranty of any kind. Microsoft further disclaims all implied warranties including, without limitation, any implied warranties of merchantability or of fitness for a particular purpose. The entire risk arising out of the use or performance of the sample scripts and documentation remains with you. In no event shall Microsoft, its authors, or anyone else involved in the creation, production, or delivery of the scripts be liable for any damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or inability to use the sample scripts or documentation, even if Microsoft has been advised of the possibility of such damages.
