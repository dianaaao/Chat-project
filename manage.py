from app.settings import app

if __name__ == "__main__":
    try:
        app.run(debug = True)
    except:
        print("Помилка")