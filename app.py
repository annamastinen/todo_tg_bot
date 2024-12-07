from flask import Flask, request, redirect
from google_auth_oauthlib.flow import Flow
import os

app = Flask(__name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Для разработки на localhost
CLIENT_SECRETS_FILE = "credentials.json"


@app.route('/callback')
def callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=request.args.get('state'),
        redirect_uri='http://localhost:8080/callback'
    )

    flow.fetch_token(authorization_response=request.url)

    # Получите токен и сохраните его (например, в базе данных или памяти)
    credentials = flow.credentials
    # Здесь вы можете сохранить credentials для дальнейшего использования

    return "Аутентификация прошла успешно! Теперь вы можете закрыть это окно."


if __name__ == '__main__':
    app.run(port=8080)

