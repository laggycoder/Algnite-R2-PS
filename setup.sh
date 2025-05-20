#!/bin/bash
set -e

PROJECT_DIR="shopsmarter_project" # Or whatever your main project folder is named
BACKEND_DIR="backend_flask"

echo "--- ShopSmarter AI Assistant Setup ---"

# Check if inside the project directory, if not, try to cd into it
if [[ ! -d "$BACKEND_DIR" && -d "../$BACKEND_DIR" ]]; then
  echo "Changing to project root directory..."
  cd ..
elif [[ ! -d "$BACKEND_DIR" ]]; then
  echo "Error: Backend directory '$BACKEND_DIR' not found. Please run this script from the project root directory ('$PROJECT_DIR')."
  exit 1
fi


# 1. Create and activate virtual environment in backend_flask
echo ""
echo "--- Setting up Python virtual environment in $BACKEND_DIR ---"
if [ ! -d "$BACKEND_DIR/venv" ]; then
  python3 -m venv "$BACKEND_DIR/venv"
  echo "Virtual environment created."
else
  echo "Virtual environment already exists."
fi

echo "To activate the virtual environment, run:"
echo "  On macOS/Linux: source $BACKEND_DIR/venv/bin/activate"
echo "  On Windows:     $BACKEND_DIR\\venv\\Scripts\\activate"
echo "Please activate it in your terminal before proceeding if this script doesn't do it for your shell."

# Attempt to activate for the current script session (might not persist for user)
# source "$BACKEND_DIR/venv/bin/activate" # This line might not work reliably across all shells when run as a script

# 2. Install Python dependencies
echo ""
echo "--- Installing Python dependencies from $BACKEND_DIR/requirements.txt ---"
# Ensure pip from venv is used if activation in script is tricky
"$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"

# 3. Create uploads directory
echo ""
echo "--- Ensuring $BACKEND_DIR/uploads directory exists ---"
mkdir -p "$BACKEND_DIR/uploads"
echo "'$BACKEND_DIR/uploads' directory is ready."

# 4. Add uploads to .gitignore if not already present
GITIGNORE_FILE=".gitignore"
UPLOADS_GITIGNORE_ENTRY="$BACKEND_DIR/uploads/"
VENV_GITIGNORE_ENTRY="$BACKEND_DIR/venv/"
PYCACHE_GITIGNORE_ENTRY="**/__pycache__"
DSSTORE_GITIGNORE_ENTRY="**/.DS_Store"


if [ ! -f "$GITIGNORE_FILE" ]; then
  echo "Creating .gitignore file..."
  touch "$GITIGNORE_FILE"
fi

if ! grep -qF "$UPLOADS_GITIGNORE_ENTRY" "$GITIGNORE_FILE"; then
  echo "Adding '$UPLOADS_GITIGNORE_ENTRY' to .gitignore"
  echo "$UPLOADS_GITIGNORE_ENTRY" >> "$GITIGNORE_FILE"
fi
if ! grep -qF "$VENV_GITIGNORE_ENTRY" "$GITIGNORE_FILE"; then
  echo "Adding '$VENV_GITIGNORE_ENTRY' to .gitignore"
  echo "$VENV_GITIGNORE_ENTRY" >> "$GITIGNORE_FILE"
fi
if ! grep -qF "$PYCACHE_GITIGNORE_ENTRY" "$GITIGNORE_FILE"; then
  echo "Adding '$PYCACHE_GITIGNORE_ENTRY' to .gitignore"
  echo "$PYCACHE_GITIGNORE_ENTRY" >> "$GITIGNORE_FILE"
fi
if ! grep -qF "$DSSTORE_GITIGNORE_ENTRY" "$GITIGNORE_FILE"; then
  echo "Adding '$DSSTORE_GITIGNORE_ENTRY' to .gitignore"
  echo "$DSSTORE_GITIGNORE_ENTRY" >> "$GITIGNORE_FILE"
fi


echo ""
echo "--- Setup Complete! ---"
echo ""
echo "Next Steps:"
echo "1. Activate the virtual environment if not already active:"
echo "   cd $BACKEND_DIR"
echo "   source venv/bin/activate  (or venv\Scripts\activate on Windows)"
echo "2. Run the Flask application:"
echo "   flask run"
echo "   (or python app.py)"
echo "3. Open your browser to http://127.0.0.1:5000"
echo ""