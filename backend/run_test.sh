#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Ensure environment variables are loaded
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Start the FastAPI server in the background
echo "Starting FastAPI server..."
python run_server.py &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 5

# Run the test
echo "Running test..."
python test_complete_pipeline.py

# Store the test exit code
TEST_EXIT_CODE=$?

# Kill the server
echo "Stopping server..."
kill $SERVER_PID

# Deactivate the virtual environment
deactivate

# Exit with the test exit code
echo "Test completed with exit code $TEST_EXIT_CODE"
exit $TEST_EXIT_CODE 