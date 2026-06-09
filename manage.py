from app.settings import app, socketio

if __name__ == "__main__":
    try:
        socketio.run(app = app, debug = True)
    except:
        print("Помилка")