// Test Cloud Connector connectivity to S/4HANA via BTP Destination Service
const https = require('https');

// Step 1: Get OAuth Token from XSUAA
function getOAuthToken() {
  return new Promise((resolve, reject) => {
    const postData = 'grant_type=client_credentials';
    
    const options = {
      hostname: 'your-subdomain.authentication.us10.hana.ondemand.com',
      port: 443,
      path: '/oauth/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + Buffer.from('clientid:clientsecret').toString('base64'),
        'Content-Length': postData.length
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const response = JSON.parse(data);
        resolve(response.access_token);
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

// Step 2: Call S/4HANA via Destination Service
async function testDestination() {
  try {
    const token = await getOAuthToken();
    
    const options = {
      hostname: 'destination-configuration.cfapps.us10.hana.ondemand.com',
      port: 443,
      path: '/destination-configuration/v1/destinations/S4HANA_ODATA/sap/opu/odata/sap/ZSALE_SERVICE/zsales_view',
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + token
      }
    };

    const req = https.request(options, (res) => {
      console.log(`Status: ${res.statusCode}`);
      
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('Response:', data.substring(0, 500));
      });
    });

    req.on('error', (error) => {
      console.error('Error:', error);
    });

    req.end();
  } catch (error) {
    console.error('Failed:', error);
  }
}

testDestination();
