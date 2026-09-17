from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting SkyCast Server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
