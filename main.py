from app import app

def main():
    app.run(debug=True, host='localhost', port=5000)


if __name__ == "__main__":
    main()
