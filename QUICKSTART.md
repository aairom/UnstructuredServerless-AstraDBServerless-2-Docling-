# Quick Start Guide

Get up and running with PDF to AstraDB in 5 minutes!

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] OpenAI API key
- [ ] AstraDB account with database created
- [ ] AstraDB API endpoint and token
- [ ] PDF file(s) to process

## 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 minute)

Create a `.env` file in the project root:

```env
API_ENDPOINT=https://your-database-id-region.apps.astra.datastax.com
APPLICATION_TOKEN=AstraCS:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Where to find these:**
- **API_ENDPOINT**: AstraDB Console → Your Database → Connect tab
- **APPLICATION_TOKEN**: AstraDB Console → Your Database → Settings → Tokens
- **OPENAI_API_KEY**: OpenAI Platform → API Keys

### Step 3: Add PDF Files (30 seconds)

```bash
# Copy your PDF files to the input folder
cp /path/to/your/file.pdf input/
```

### Step 4: Run Application (1 minute)

#### Option A: Console Application
```bash
python app_console_docling.py
```

#### Option B: GUI Application
```bash
# Direct launch
streamlit run app_gui_docling.py

# OR detached mode
./scripts/launch_gui.sh
```

### Step 5: Query Your Documents (30 seconds)

**Console**: Queries run automatically

**GUI**: 
1. Open http://localhost:8501
2. Click "🚀 Process PDF"
3. Enter your question
4. Click "🔍 Search"

## Example Queries

Try these questions:
- "What is the main topic of this document?"
- "Summarize the key findings"
- "What are the conclusions?"

## What's Next?

- 📖 Read the [README.md](README.md) for detailed information
- ⚙️ Check [CONFIGURATION.md](Docs/CONFIGURATION.md) for customization
- 🔧 Review [INSTALLATION.md](Docs/INSTALLATION.md) for troubleshooting

## Common Issues

### "No module named 'docling'"
```bash
pip install -r requirements.txt
```

### "Missing environment variables"
Check your `.env` file has all three variables set correctly.

### "No PDF files found"
Ensure PDF files are in the `input/` folder.

### GUI won't start
```bash
# Check if port is in use
lsof -i :8501

# Try different port
./scripts/launch_gui.sh 8502
```

## Stop GUI Application

```bash
# Use the stop script
./scripts/stop_gui.sh

# OR find and kill process
kill $(cat logs/streamlit.pid)
```

## Need Help?

1. Check the logs in `logs/` folder
2. Review documentation in `Docs/` folder
3. Verify all credentials are correct

---

**Ready to process PDFs! 🚀**