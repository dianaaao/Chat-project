from app.settings import app, socketio

if __name__ == "__main__":
    try:
        socketio.run(app = app, port= 8080, debug = True) #host= "0.0.0.0", 
    except:
        print("Помилка")