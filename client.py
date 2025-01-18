import requests
import pickle
from phe import paillier
import time

# Fetch the server's public key
try:
    response = requests.get("http://127.0.0.1:5000/get_public_key")
    if response.status_code == 200:
        public_key = pickle.loads(response.content)  # Load the server's public key
    else:
        print(f"Error fetching public key: {response.content}")
        exit()
except requests.exceptions.RequestException as e:
    print(f"Error communicating with the server: {str(e)}")
    exit()

# Desired record index
desired_index = 2  # Example: Requesting "Record_2"

# Create a one-hot query vector
query = [0] * 10  # For 10 records
query = [0] * 100  # For 100 records
query = [0] * 1000  # For 1000 records  # Adjust this to match the number of records in the database
query[desired_index] = 1

# Encrypt the query vector using the server's public key
start_enc_time = time.time()
encrypted_query = [public_key.encrypt(val) for val in query]
end_enc_time = time.time()
encryption_time = (end_enc_time - start_enc_time) * 1000  # Convert to ms

try:
    # Serialize the encrypted query
    serialized_query = pickle.dumps(encrypted_query)

    # Measure query size
    query_size = len(serialized_query)

    # Send the encrypted query to the server
    start_req_time = time.time()
    response = requests.post(
        "http://127.0.0.1:5000/submit_query",
        data=serialized_query
    )
    end_req_time = time.time()
    response_time = (end_req_time - start_req_time) * 1000  # Convert to ms

    # Check if the response status is OK
    if response.status_code == 200:
        # Receive and deserialize the encrypted response
        encrypted_response = pickle.loads(response.content)

        # Measure response size
        response_size = len(response.content)

        # Log results
        print("Raw response content:", response.content)
        print(f"Encrypted response received successfully: {encrypted_response}")
        print(f"Query size (bytes): {query_size}")
        print(f"Response size (bytes): {response_size}")
        print(f"Encryption time: {encryption_time:.2f} ms")
        print(f"Response time (round trip): {response_time:.2f} ms")
    else:
        print(f"Error from server: {response.content}")

except requests.exceptions.RequestException as e:
    print(f"Error communicating with the server: {str(e)}")
except pickle.UnpicklingError:
    print("Error: Received unexpected or malformed response from the server.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
