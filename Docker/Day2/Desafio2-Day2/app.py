from flask import Flask, request, jsonify

app = Flask (__name__)

PORT = 3000

@app.route('/', methods=['GET'])
def home():
  return "Ok", 200

@app.errorhandler(404)
def not_found(e):
  return "Not found", 404

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=PORT)