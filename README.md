# 🎯 Wildberries Slot Monitor

Professional-grade web application for monitoring and auto-booking delivery slots at Wildberries warehouses via their API.

## 🌟 Features

- **Real-time Monitoring**: Continuously checks multiple warehouses for available slots
- **Smart Filtering**: Configure acceptable coefficient thresholds and date ranges
- **Auto-Booking**: Automatically books slots matching your criteria
- **Telegram Notifications**: Get instant alerts when slots are found or booked
- **Professional Dashboard**: Clean Streamlit UI with real-time activity logs
- **Robust Error Handling**: Gracefully handles API errors, rate limits, and network issues
- **Rate Limiting Protection**: Random delays between requests to avoid API bans

## 📋 Prerequisites

- Python 3.11 or higher
- Wildberries Supplier API token
- (Optional) Telegram Bot for notifications

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd wildberries-slot-monitor

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Your API Credentials

#### Wildberries API Token
1. Log in to your Wildberries Supplier account
2. Navigate to Settings → API
3. Generate a new API token with "Supplies" permissions
4. Copy the token (keep it secure!)

#### Telegram Bot (Optional)
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the bot token
4. Search for `@userinfobot` and send `/start`
5. Copy your chat ID

### 3. Run the Application

```bash
streamlit run main.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Configure API Access

1. **WB API Token**: Paste your Wildberries API token
2. Click "Test WB Connection" to verify and load warehouses
3. **Telegram** (optional): Enter bot token and chat ID
4. Click "Test Telegram" to verify notifications

### Step 2: Create a Monitoring Task

1. **Select Warehouses**: Choose one or more warehouses to monitor
2. **Date Range**: Set start and end dates for slot search
3. **Max Coefficient**: Set the maximum acceptable coefficient (e.g., 5.0 for ≤x5)
4. **Shipment Type**: Choose "box" or "monopallet"
5. **Mode**:
   - 🔔 **Notify Only**: Sends Telegram alert when slot found
   - 🤖 **Auto-Book**: Automatically books the slot

6. Click "Create Task"

### Step 3: Start Monitoring

1. Click "▶️ Start Monitoring"
2. The engine will continuously check for slots every 30-60 seconds
3. Watch the Activity Log for real-time updates

## 📁 Project Structure

```
wildberries-slot-monitor/
├── main.py              # Streamlit UI and main application
├── wb_api.py            # Wildberries API client
├── utils.py             # Telegram notifications and logging
├── models.py            # Pydantic data models
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🏗️ Architecture

### Components

1. **WildberriesAPI** (`wb_api.py`)
   - Async HTTP client using `httpx`
   - Handles authentication, rate limiting, and errors
   - Methods: `get_warehouses()`, `get_available_slots()`, `book_slot()`

2. **TelegramNotifier** (`utils.py`)
   - Sends formatted alerts via Telegram Bot API
   - Methods for different notification types (slot found, booking success/failure)

3. **Logger** (`utils.py`)
   - In-memory logging for the dashboard
   - Automatic log rotation (max 500 entries)

4. **Streamlit Dashboard** (`main.py`)
   - Configuration interface
   - Task management
   - Monitoring controls
   - Real-time activity log

## 🔧 API Endpoints Used

The application uses the following Wildberries Suppliers API endpoints:

```
Base URL: https://supplies-api.wildberries.ru

GET  /api/v1/warehouses              # List warehouses
GET  /api/v1/acceptance/coefficients # Get available slots
POST /api/v1/acceptance              # Book a slot
```

### Official Documentation

- **Wildberries API Docs**: https://openapi.wildberries.ru/
- **Supplies API**: Look for "Поставки" (Supplies) section

## ⚙️ Configuration

### API Rate Limiting

The application implements intelligent rate limiting:

- Random delay between **30-60 seconds** between polling cycles
- 2-second delay between checking multiple warehouses in one task
- Exponential backoff on 429 (Too Many Requests) errors

Adjust in `main.py`:
```python
POLL_INTERVAL_MIN = 30  # Minimum seconds between checks
POLL_INTERVAL_MAX = 60  # Maximum seconds between checks
```

### Monitoring Parameters

- **Max Coefficient**: 0.0 to 20.0 (slider in UI)
- **Date Range**: Up to 30 days recommended
- **Warehouses**: Can monitor multiple warehouses simultaneously

## 🛡️ Error Handling

The application handles various error scenarios:

- **Invalid API Token**: Clear error message with instructions
- **Network Errors**: Automatic retry logic
- **Rate Limiting (429)**: Respects Retry-After header
- **Server Errors (5xx)**: Logs error and continues monitoring
- **Booking Conflicts**: Notifies user via Telegram and logs

## 🚨 Production Deployment

### Important Note

The current implementation runs monitoring while the Streamlit page is active. For **production 24/7 monitoring**, consider:

1. **Separate Background Worker**:
   ```bash
   # Use Celery, APScheduler, or similar
   pip install celery redis
   ```

2. **Deploy on a Server**:
   - Use Docker for containerization
   - Deploy on AWS, Azure, or DigitalOcean
   - Use PM2 or systemd for process management

3. **Database**:
   - Store tasks and logs in PostgreSQL or MongoDB
   - Current version uses in-memory storage (session state)

### Docker Deployment (Example)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🐛 Troubleshooting

### "Authentication failed" Error
- Verify your WB API token is correct
- Ensure token has "Supplies" permissions
- Check if token hasn't expired

### "No warehouses loaded"
- Click "Test WB Connection" first
- Check your internet connection
- Verify API endpoint is accessible

### Telegram Notifications Not Working
- Verify bot token and chat ID
- Check that you've started a conversation with the bot
- Use "Test Telegram" button to diagnose

### Slots Found But Not Booking
- Check that mode is set to "Auto-Book"
- Verify you have permission to book slots
- Check logs for specific error messages

## 📊 Performance Tips

1. **Limit Warehouses**: Monitor only warehouses you're interested in
2. **Reasonable Date Ranges**: 7-14 days is optimal
3. **Coefficient Threshold**: Set realistic values (1.0-5.0 for best slots)
4. **Network**: Ensure stable internet connection

## 🔐 Security Best Practices

1. **Never commit API tokens** to version control
2. **Use environment variables** for sensitive data
3. **Rotate tokens** regularly
4. **Limit API permissions** to only what's needed
5. **Use HTTPS** when deployed to production

## 📝 License

This project is for educational and personal use. Ensure compliance with Wildberries' Terms of Service and API usage policies.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 💡 Future Enhancements

- [ ] Database integration (PostgreSQL)
- [ ] Multi-user support
- [ ] Slot booking history
- [ ] Advanced filtering (by region, warehouse type)
- [ ] Email notifications
- [ ] Mobile app
- [ ] Analytics dashboard
- [ ] Webhook support

## 📞 Support

For issues related to:
- **Wildberries API**: Contact WB support
- **This Application**: Open an issue in the repository

---

**⚠️ Disclaimer**: This tool is provided as-is. Always test in a non-production environment first. The developers are not responsible for any issues arising from the use of this software.

**Happy slot hunting! 🎯**
