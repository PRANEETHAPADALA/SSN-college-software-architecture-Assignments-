GreyNoise Community API ETL Connector
Author: [YOUR NAME]
Roll Number: [YOUR ROLL NUMBER]
Course: Software Architecture - SSN CSE (Kyureeus EdTech)

📖 Overview
This ETL (Extract, Transform, Load) connector integrates with the GreyNoise Community API to fetch IP threat intelligence data and stores it in MongoDB. GreyNoise analyzes internet background noise to identify malicious, benign, and unknown IP addresses scanning the internet.

🎯 Data Provider: GreyNoise Community API
API Details
Provider: GreyNoise
API Type: Community API (Free tier)
Base URL: https://api.greynoise.io/v3/community
Endpoint: /v3/community/{ip}
Authentication: API Key (Header-based)
Rate Limits:
Community API: 50 requests per day
10 requests per minute
Documentation: https://docs.greynoise.io/docs/community-api
Data Returned
The API provides the following information for each IP:

noise: Boolean indicating if IP is "noisy" (mass-scanning the internet)
riot: Boolean indicating if IP is from a known benign service
classification: Category (malicious, benign, unknown)
name: Name of the organization/service
link: Reference link for more information
last_seen: Last time the IP was observed
message: Additional context about the IP
🏗️ ETL Pipeline Architecture
1. Extract
Connects to GreyNoise Community API
Passes API key in request headers
Retrieves JSON data for specified IP addresses
Handles rate limiting with exponential backoff
Manages error responses (404, 429, timeouts)
2. Transform
Cleans and structures raw API response
Adds metadata:
Query timestamp
Ingestion timestamp
Data source identifier
Normalizes field names for MongoDB compatibility
Preserves complete raw response for audit purposes
3. Load
Stores transformed data in MongoDB collection
Uses upsert operation (update existing or insert new)
Ensures idempotency (IP address as unique key)
Adds ingestion timestamps for tracking
📋 Prerequisites
1. GreyNoise API Key
Visit https://www.greynoise.io/
Create a free account
Navigate to Account → API Key
Copy your Community API key
2. MongoDB Installation
Choose one of the following:

Option A: Local MongoDB

bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS
Option B: MongoDB Atlas (Cloud)

Visit https://www.mongodb.com/cloud/atlas
Create free account and cluster
Get connection string (mongodb+srv://...)
3. Python Environment
Python 3.7 or higher
pip package manager
🚀 Setup Instructions
Step 1: Clone Repository
bash
git clone <repository-url>
cd SSN-college-software-architecture-Assignments
git checkout -b <your-name-rollnumber>
Step 2: Install Dependencies
bash
pip install -r requirements.txt
Step 3: Configure Environment Variables
Copy the template file:
bash
cp .env.template .env
Edit .env file with your credentials:
bash
# Open in your favorite editor
nano .env  # or vim, code, etc.
Fill in your credentials:
env
GREYNOISE_API_KEY=your_actual_api_key_here
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=etl_database
MONGODB_COLLECTION=greynoise_raw
Important: Never commit the .env file to Git!

Step 4: Verify .gitignore
Ensure .env is listed in .gitignore:

bash
echo ".env" >> .gitignore
💻 Usage
Basic Execution
bash
python etl_connector.py
Modify IP Addresses to Query
Edit the ip_addresses list in etl_connector.py:

python
ip_addresses = [
    "8.8.8.8",          # Your IPs here
    "1.1.1.1",
    "45.142.212.61",
]
Example Output
============================================================
GreyNoise Community API ETL Pipeline
============================================================
Connecting to MongoDB...
✓ Connected to MongoDB: etl_database.greynoise_raw

============================================================
Processing IP: 8.8.8.8
============================================================

Extracting data for IP: 8.8.8.8
✓ Successfully extracted data for 8.8.8.8
Transforming data...
✓ Data transformed successfully
Loading data into MongoDB...
✓ Inserted new document with ID: 507f1f77bcf86cd799439011

============================================================
ETL Pipeline Execution Summary
============================================================
Total IPs processed: 4
Successful: 4
Failed: 0
============================================================
🗃️ MongoDB Collection Schema
Collection Name: greynoise_raw

Document Structure:

json
{
  "_id": ObjectId("..."),
  "ip_address": "8.8.8.8",
  "query_timestamp": ISODate("2025-10-31T10:30:00.000Z"),
  "ingestion_timestamp": "2025-10-31T10:30:00.123456",
  "data_source": "greynoise_community_api",
  "noise": false,
  "riot": true,
  "classification": "benign",
  "name": "Google Public DNS",
  "link": "https://viz.greynoise.io/riot/8.8.8.8",
  "last_seen": "2025-10-30",
  "message": "Google DNS Service",
  "raw_response": { ... }
}
🧪 Testing & Validation
Test Cases Covered
✅ Valid IP address query
✅ Invalid/Not found IP address (404 handling)
✅ Rate limit handling (429 response)
✅ Network timeout handling
✅ MongoDB connection failures
✅ Invalid JSON response handling
✅ Empty payload handling
✅ Duplicate IP upsert logic
Manual Testing
bash
# Test with various IPs
python etl_connector.py

# Check MongoDB data
mongo
use etl_database
db.greynoise_raw.find().pretty()
🔒 Security Best Practices
✅ API keys stored in .env file (not in code)
✅ .env added to .gitignore
✅ Environment variables loaded using python-dotenv
✅ No hardcoded credentials in any file
✅ Connection timeouts implemented
✅ Error handling for all API calls
📊 MongoDB Query Examples
javascript
// Find all malicious IPs
db.greynoise_raw.find({ classification: "malicious" })

// Find all benign IPs
db.greynoise_raw.find({ riot: true })

// Find IPs ingested today
db.greynoise_raw.find({ 
  query_timestamp: { 
    $gte: ISODate("2025-10-31T00:00:00Z") 
  } 
})

// Count by classification
db.greynoise_raw.aggregate([
  { $group: { _id: "$classification", count: { $sum: 1 } } }
])
Troubleshooting
Issue: "GREYNOISE_API_KEY not found"
Solution: Ensure .env file exists and contains the API key

Issue: "Failed to connect to MongoDB"
Solution:

Check if MongoDB is running: sudo systemctl status mongodb
Verify connection string in .env
For Atlas, whitelist your IP address
Issue: "Rate limit exceeded"
Solution:

Community API has 50 requests/day limit
Script automatically waits 60 seconds when rate limited
Reduce number of IPs in test list
Issue: "404 Not Found"
Solution: IP address not in GreyNoise database (normal behavior for some IPs)

Additional Resources
GreyNoise API Documentation
PyMongo Tutorial
Python dotenv Documentation
Requests Library Guide

Author Information
Name: Padala Praneetha
Roll Number: 3122225001089
Institution: SSN College of Engineering
Department: Computer Science and Engineering
Program: Kyureeus EdTech - Software Architecture

License
This project is for educational purposes as part of the SSN CSE Software Architecture course.


