from main import app, start_bogo_sort

app.logger.info("WSGI entry point: Initializing application...")
start_bogo_sort()
app.logger.info("WSGI entry point: Application initialized successfully.")
