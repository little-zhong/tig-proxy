from flask import Flask, request, jsonify
from curl_cffi import requests
import logging

app = Flask(__name__)

# 设置日志记录
logging.basicConfig(
    filename="request_logs.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

API_BASE_URL = "https://mainnet-api.tig.foundation"


def log_request_response(req_data, resp_data):
    logging.info(f"Incoming request: {req_data}")
    logging.info(f"API response: {resp_data}")


@app.route("/<path:endpoint>", methods=["GET", "POST"])
def proxy_request(endpoint):
    try:
        # 准备请求数据
        api_url = f"{API_BASE_URL}/{endpoint}"
        req_data = {
            "method": request.method,
            "url": request.url,
            "body": request.json if request.is_json else request.data.decode(),
        }

        # 发送请求
        api_response = requests.request(
            method=request.method,
            url=api_url,
            params=request.args if request.method == "GET" else None,
            json=request.json if request.method == "POST" else None,
            impersonate="chrome",
        )

        # 准备响应数据
        resp_data = (
            api_response.json()
            if api_response.headers.get("Content-Type") == "application/json"
            else api_response.text
        )

        # 记录请求和响应
        log_request_response(req_data, resp_data)

        return jsonify(resp_data), api_response.status_code

    except Exception as e:
        logging.exception(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5151, debug=True)
