from flask import Flask, request, jsonify
import requests
import os
from loguru import logger

app = Flask(__name__)

# Set up logging: one file per day, keep for 7 days
logger.add("logs/{time:YYYY-MM-DD}.log", rotation="1 week", retention="7 days")

API_BASE_URL = os.environ.get("API_BASE_URL", "https://mainnet-api.tig.foundation")


def log_request_response(req_data, resp_data):
    logger.info(f"Incoming request: {req_data}")
    logger.info(f"API response: {resp_data}")


@app.route("/<path:endpoint>", methods=["GET", "POST"])
def proxy_request(endpoint):
    try:
        # Prepare request data
        api_url = f"{API_BASE_URL}/{endpoint}"
        req_data = {
            "method": request.method,
            "url": request.url,
            "body": request.json if request.is_json else request.data.decode(),
            "headers": dict(request.headers),
        }

        # Send request
        api_response = requests.request(
            method=request.method,
            url=api_url,
            params=request.args if request.method == "GET" else None,
            json=request.json if request.method == "POST" else None,
            headers=(
                {"X-Api-Key": request.headers.get("X-Api-Key")}
                if req_data["headers"].get("X-Api-Key")
                else None
            ),
            timeout=10,  # Add 10 seconds timeout
        )

        # Prepare response data
        resp_data = (
            api_response.json()
            if api_response.headers.get("Content-Type") == "application/json"
            else api_response.text
        )

        # Log request and response
        log_request_response(req_data, resp_data)

        return jsonify(resp_data), api_response.status_code

    except requests.RequestException as e:
        logger.exception(f"API request error: {e}")
        return jsonify({"error": "Failed to reach the API server"}), 503
    except ValueError as e:
        logger.exception(f"JSON parsing error: {e}")
        return jsonify({"error": "Invalid JSON in response"}), 502
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5151, debug=False)
