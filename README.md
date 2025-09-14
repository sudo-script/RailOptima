# RailOptima 🚆

RailOptima is an intelligent decision-support system for railway traffic management. It optimizes train precedence, crossings, and scheduling while dynamically re-optimizing under disruptions. Built on the FRPS stack (FastAPI, React, Python, SQL), it boosts efficiency, punctuality, and controller decision-making.

## ✨ Features

- **Conflict Resolution**: Resolves conflicts in train departures
- **Schedule Validation**: Validates optimized schedules
- **Visualizations**: Provides comprehensive visualizations
- **Execution Logs**: Maintains detailed execution logs
- **Real-time Optimization**: Dynamic re-optimization under disruptions
- **Web Interface**: Modern React-based frontend
- **REST API**: FastAPI-based backend with automatic documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm (comes with Node.js)

### Automated Setup (Recommended)

**Windows:**
```cmd
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh && ./install.sh
```

**Cross-platform:**
```bash
python setup-environment.py
```

### Manual Setup
See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed instructions.

### Docker Setup
```bash
# Production
docker-compose up -d

# Development
docker-compose --profile dev up
```

## 🏃‍♂️ Running the Application

After setup, start the application:

**Windows:**
```cmd
start-railoptima.bat
# or
start-railoptima.ps1
```

**Linux/macOS:**
```bash
./start-railoptima.sh
```

**Access URLs:**
- Frontend: http://localhost:9002
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📂 Project Structure
```
RailOptima/
├── optimizer/              # Core optimization logic
│   ├── optimizer_schedule.py
│   ├── validate_schedule.py
│   ├── visualize_schedule.py
│   └── log_report.py
├── support/               # API support and utilities
│   ├── api_support/       # FastAPI backend
│   └── monitoring/        # System monitoring
├── SIHH-main/            # React frontend application
├── Audit/                # Audit and validation tools
├── docs/                 # Documentation
├── reports/              # Generated reports and logs
├── docker/               # Docker configuration
├── requirements.txt      # Python dependencies
├── env.example          # Environment template
├── setup-environment.py # Python setup script
├── install.sh           # Unix installation script
├── install.bat          # Windows installation script
└── docker-compose.yml   # Docker services
```

## 📚 Documentation

- [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Comprehensive setup guide
- [SETUP_SUMMARY.md](SETUP_SUMMARY.md) - Setup files overview
- [docs/](docs/) - Detailed module documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 🛠️ Development

### Environment Setup
1. Run the setup script for your platform
2. Activate the virtual environment
3. Start the development servers

### Adding Dependencies
- **Python**: Add to `requirements.txt`
- **Node.js**: Add to `SIHH-main/package.json`

### Code Structure
- **Backend**: FastAPI application in `support/api_support/`
- **Frontend**: Next.js application in `SIHH-main/`
- **Core Logic**: Optimization algorithms in `optimizer/`

## 🐳 Docker Support

The project includes comprehensive Docker support:

- **Production**: Multi-stage builds with Nginx
- **Development**: Hot reload with volume mounting
- **Services**: API, frontend, and optional database
- **Orchestration**: Docker Compose for easy deployment

## 🔧 Configuration

Environment variables are configured in `.env` file:

```env
API_HOST=localhost
API_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_PORT=9002
DEBUG=true
ENVIRONMENT=development
```

## 📊 Monitoring

The system includes built-in monitoring:
- Health checks for all services
- Performance metrics
- Log aggregation
- Error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:
1. Check the [troubleshooting guide](ENVIRONMENT_SETUP.md#troubleshooting)
2. Review logs in the `reports/` directory
3. Ensure all prerequisites are installed correctly

---

**Built with ❤️ for efficient railway traffic management**