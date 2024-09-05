from flask import Flask, request, jsonify
from curl_cffi import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    filename="request_logs.log", level=logging.INFO, format="%(asctime)s %(message)s"
)

# Target API base URL
API_BASE_URL = "https://mainnet-api.tig.foundation"


# Mapping incoming request to the target API
@app.route("/<path:endpoint>", methods=["GET", "POST"])
def proxy_request(endpoint):
    try:
        # Log the incoming request
        incoming_data = {
            # "headers": dict(request.headers),
            "method": request.method,
            "url": request.url,
            "body": request.json if request.is_json else request.data.decode(),
        }
        logging.info(f"Incoming request: {incoming_data}")

        # Prepare the request to the target API
        api_url = f"{API_BASE_URL}/{endpoint}"

        if request.method == "GET":
            # Forward GET request
            api_response = requests.get(
                api_url,
                # headers=request.headers,
                params=request.args,
                impersonate="chrome",
            )
        elif request.method == "POST":
            # Forward POST request
            api_response = requests.post(
                api_url,
                # headers=request.headers,
                json=request.json,
                impersonate="chrome",
            )
        # Log the API response
        response_data = {
            "status_code": api_response.status_code,
            "headers": dict(api_response.headers),
            "body": (
                api_response.json()
                if api_response.headers.get("Content-Type") == "application/json"
                else api_response.text
            ),
        }
        logging.info(f"API response: {response_data}")

        # Return the response from the API to the client
        return jsonify(response_data), api_response.status_code

    except Exception as e:
        logging.exception(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5151, debug=True)
