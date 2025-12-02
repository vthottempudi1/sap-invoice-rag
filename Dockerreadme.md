# Using OpenSSL
openssl rand -hex 16

# Save this key in your docker-compose.yml

# Start n8n container
docker-compose up -d

# Check logs
docker-compose logs -f n8n

# Verify it's running
docker ps


# Step 4: Access n8n
Open browser: http://localhost:5678
Login with credentials from docker-compose.yml

# Step 1: Login to Cloud Foundry
bash# Login to SAP BTP Cloud Foundry
cf login -a https://api.cf.us10.hana.ondemand.com

# Enter your credentials
Email: your-email@example.com
Password: your-password

# Select org and space
cf target -o "your-org" -s "your-space"

# Create service instance
cf create-service destination lite n8n-destination

# Check service status
cf service n8n-data

# Create service key for credentials
cf create-service-key n8n-destination n8n-key

# Get credentials
cf service-key n8n-destination n8n-key

# Step 3: Common SAP BTP Services to Connect
# A. Destination Service
'''bash
cf create-service destination lite n8n-destination
cf create-service-key n8n-destination n8n-dest-key
cf service-key n8n-destination n8n-dest-key
'''
# B. XSUAA (Authentication)
''' bash
cf create-service xsuaa application n8n-xsuaa
cf create-service-key n8n-xsuaa n8n-xsuaa-key
cf service-key n8n-xsuaa n8n-xsuaa-key
'''
# C. SAP HANA Cloud
'''bash
cf create-service hana hdi-shared n8n-hana
cf create-service-key n8n-hana n8n-hana-key
cf service-key n8n-hana n8n-hana-key
'''
# D. Business Application Studio
'''bash
cf create-service business-application-studio standard-edition n8n-bas
cf create-service-key n8n-bas n8n-bas-key
'''