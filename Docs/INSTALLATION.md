# Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: macOS, Linux, or Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Internet**: Required for API calls

### Required Accounts
1. **OpenAI Account**
   - Sign up at https://platform.openai.com
   - Generate API key
   - Ensure sufficient credits

2. **AstraDB Account**
   - Sign up at https://astra.datastax.com
   - Create a serverless database
   - Generate application token

## Step-by-Step Installation

### 1. Python Environment Setup

#### Check Python Version
```bash
python --version
# Should be 3.9 or higher
```

#### Create Virtual Environment
```bash
# Navigate to project directory
cd UnstructuredServerless-AstraDBServerless-2-Docling

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Configure Environment Variables

#### Create .env File
```bash
# Copy template (if exists) or create new
touch .env
```

#### Add Configuration
Edit `.env` file with your credentials:

```env
# AstraDB Configuration
API_ENDPOINT=https://your-database-id-region.apps.astra.datastax.com
APPLICATION_TOKEN=AstraCS:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI Configuration
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Get AstraDB Credentials

1. Log in to [AstraDB Console](https://astra.datastax.com)
2. Select your database
3. Go to "Connect" tab
4. Copy the API Endpoint
5. Generate a new token with "Database Administrator" role
6. Copy the token

#### Get OpenAI API Key

1. Log in to [OpenAI Platform](https://platform.openai.com)
2. Navigate to API Keys section
3. Create new secret key
4. Copy and save the key securely

### 4. Prepare Input Directory

```bash
# Create input directory if not exists
mkdir -p input

# Add your PDF files
cp /path/to/your/file.pdf input/
```

### 5. Verify Installation

#### Test Console Application
```bash
python app_console_docling.py
```

Expected output:
- PDF processing messages
- Document extraction confirmation
- AstraDB connection success
- Query results

#### Test GUI Application
```bash
streamlit run app_gui_docling.py
```

Expected behavior:
- Browser opens automatically
- Application loads at http://localhost:8501
- Configuration shows as valid

## Troubleshooting Installation

### Common Issues

#### 1. Python Version Mismatch
**Error**: `Python 3.9 or higher required`

**Solution**:
```bash
# Install Python 3.9+ from python.org
# Or use pyenv
pyenv install 3.9.0
pyenv local 3.9.0
```

#### 2. Pip Installation Fails
**Error**: `Could not install packages`

**Solution**:
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Try installing with verbose output
pip install -r requirements.txt -v
```

#### 3. Docling Installation Issues
**Error**: `Failed building wheel for docling`

**Solution**:
```bash
# Install build dependencies
pip install build wheel

# Install docling separately
pip install docling --no-cache-dir
```

#### 4. Environment Variables Not Loading
**Error**: `Missing environment variables`

**Solution**:
```bash
# Verify .env file exists
ls -la .env

# Check file contents (without exposing secrets)
cat .env | grep -v "KEY\|TOKEN"

# Reinstall python-dotenv
pip install --upgrade python-dotenv
```

#### 5. AstraDB Connection Fails
**Error**: `Connection timeout` or `Authentication failed`

**Solution**:
- Verify API endpoint format
- Check token has correct permissions
- Ensure database is active (not hibernated)
- Test connection with astra.py sample

#### 6. OpenAI API Errors
**Error**: `Invalid API key` or `Rate limit exceeded`

**Solution**:
- Verify API key is correct
- Check account has credits
- Review usage limits
- Wait if rate limited

### Platform-Specific Issues

#### macOS
```bash
# If SSL certificate errors occur
pip install --upgrade certifi

# If command line tools missing
xcode-select --install
```

#### Linux
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev build-essential

# For PDF processing
sudo apt-get install poppler-utils
```

#### Windows
```powershell
# Use PowerShell as administrator
# Install Visual C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/downloads/
```

## Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] .env file created with valid credentials
- [ ] Input directory exists with PDF files
- [ ] Console application runs without errors
- [ ] GUI application accessible in browser
- [ ] AstraDB connection successful
- [ ] OpenAI API responding

## Next Steps

After successful installation:

1. **Read the README.md** for usage instructions
2. **Review Docs/CONFIGURATION.md** for advanced settings
3. **Test with sample PDF** from input folder
4. **Explore both applications** (console and GUI)

## Getting Help

If you encounter issues not covered here:

1. Check application logs in `logs/` folder
2. Review error messages carefully
3. Verify all credentials are correct
4. Ensure all services are accessible
5. Check project documentation in `Docs/` folder

## Updating

To update the project:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart applications
```

---

**Installation complete! Ready to process PDFs with Docling and AstraDB.**