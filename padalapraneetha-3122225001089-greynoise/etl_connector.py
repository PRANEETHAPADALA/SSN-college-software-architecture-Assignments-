import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import requests
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import json
import time

load_dotenv()

class GreyNoiseETL:
    def __init__(self):
        self.api_key = os.getenv('GREYNOISE_API_KEY')
        self.base_url = "https://api.greynoise.io/v3/community"
        self.mongo_uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('MONGODB_DATABASE', 'etl_database')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'greynoise_raw')
        self._validate_credentials()
        self.client = None
        self.db = None
        self.collection = None

    def _validate_credentials(self):
        if not self.api_key:
            raise ValueError("GREYNOISE_API_KEY not found in environment variables")
        if not self.mongo_uri:
            raise ValueError("MONGODB_URI not found in environment variables")

    def connect_mongodb(self):
        try:
            print("Connecting to MongoDB...")
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            print(f"✓ Connected to MongoDB: {self.db_name}.{self.collection_name}")
            return True
        except ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            print(f"✗ MongoDB connection error: {e}")
            return False

    def extract(self, ip_address):
        headers = {
            'key': self.api_key,
            'Accept': 'application/json'
        }
        endpoint = f"{self.base_url}/{ip_address}"
        try:
            print(f"\nExtracting data for IP: {ip_address}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 429:
                print("✗ Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return self.extract(ip_address)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Successfully extracted data for {ip_address}")
                return data
            elif response.status_code == 404:
                print(f"✗ IP address {ip_address} not found in GreyNoise database")
                return None
            else:
                print(f"✗ API request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.Timeout:
            print("✗ Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error: {e}")
            return None
        except json.JSONDecodeError:
            print("✗ Failed to parse JSON response")
            return None

    def transform(self, raw_data, ip_address):
        if not raw_data:
            return None
        print("Transforming data...")
        transformed_data = {
            'ip_address': ip_address,
            'query_timestamp': datetime.utcnow(),
            'ingestion_timestamp': datetime.utcnow().isoformat(),
            'data_source': 'greynoise_community_api',
            'noise': raw_data.get('noise', False),
            'riot': raw_data.get('riot', False),
            'classification': raw_data.get('classification', 'unknown'),
            'name': raw_data.get('name', ''),
            'link': raw_data.get('link', ''),
            'last_seen': raw_data.get('last_seen', ''),
            'message': raw_data.get('message', ''),
            'raw_response': raw_data
        }
        print("✓ Data transformed successfully")
        return transformed_data

    def load(self, transformed_data):
        if not transformed_data:
            print("✗ No data to load")
            return False
        try:
            print("Loading data into MongoDB...")
            result = self.collection.update_one(
                {'ip_address': transformed_data['ip_address']},
                {'$set': transformed_data},
                upsert=True
            )
            if result.upserted_id:
                print(f"✓ Inserted new document with ID: {result.upserted_id}")
            else:
                print(f"✓ Updated existing document for IP: {transformed_data['ip_address']}")
            return True
        except PyMongoError as e:
            print(f"✗ MongoDB insertion error: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error during load: {e}")
            return False

    def run_etl(self, ip_addresses):
        print("=" * 60)
        print("GreyNoise Community API ETL Pipeline")
        print("=" * 60)
        if not self.connect_mongodb():
            print("\n✗ ETL Pipeline failed: Could not connect to MongoDB")
            return
        successful = 0
        failed = 0
        for ip in ip_addresses:
            print(f"\n{'=' * 60}")
            print(f"Processing IP: {ip}")
            print(f"{'=' * 60}")
            raw_data = self.extract(ip)
            if raw_data:
                transformed_data = self.transform(raw_data, ip)
                if self.load(transformed_data):
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1
            time.sleep(1)
        print("\n" + "=" * 60)
        print("ETL Pipeline Execution Summary")
        print("=" * 60)
        print(f"Total IPs processed: {len(ip_addresses)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print("=" * 60)

    def close(self):
        if self.client:
            self.client.close()
            print("\n✓ MongoDB connection closed")

def main():
    ip_addresses = [
        "8.8.8.8",
        "1.1.1.1",
        "45.142.212.61",
        "185.220.101.1",
    ]
    try:
        etl = GreyNoiseETL()
        etl.run_etl(ip_addresses)
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✗ ETL Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    finally:
        try:
            etl.close()
        except:
            pass

if __name__ == "__main__":
    main()
