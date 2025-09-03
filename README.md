# PersonaForge.AI - LinkedIn Automation Tool

🚀 **Local-first, privacy-focused LinkedIn content automation system**

PersonaForge.AI is a comprehensive multi-agent system designed to help professionals create, schedule, and optimize LinkedIn content while keeping all data private and secure on your local machine.

## 🌟 Features

### 🤖 Multi-Agent System
- **Content Agent**: Generates engaging LinkedIn posts, captions, and ideas
- **Image Agent**: Creates relevant visuals (infographics, charts, quotes, timelines)
- **Prompt Agent**: Structures prompts for consistent, high-quality generation

### 📊 Personalized Post Monitoring
- Analyzes past LinkedIn posts to adapt tone, style, and topics
- Tracks engagement metrics to refine future content
- Learns from your posting patterns and performance

### 👤 User-Centric Input System
- Collects information about your work, skills, and career goals
- Adapts content generation to your professional brand
- Maintains context-aware post creation

### 📅 Intelligent Scheduling
- Supports the strategic 3-month posting framework:
  - **Mini Projects**: Every 15 days
  - **Main Projects**: Monthly
  - **Capstone Projects**: End of 3 months
- Optimal timing based on LinkedIn best practices
- Custom scheduling options

### 🔒 Privacy-First Design
- **100% Local**: No cloud storage, all processing on your machine
- **Optional Encryption**: Protect sensitive data with local encryption
- **No External APIs**: Your data never leaves your computer
- **Secure Storage**: Local SQLite database with privacy controls

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Ollama (for local AI processing)

### Quick Start (Automated)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PersonaForge.Ai
   ```

2. **Run the installation script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Start the application**
   ```bash
   python startup.py
   ```

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai for instructions)
   ollama pull llama3.2  # or your preferred model
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Test the system**
   ```bash
   python test_system.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

### Troubleshooting Installation

**Missing Dependencies Error**
```bash
# Install all required packages
pip install -r requirements.txt

# For specific missing packages:
pip install aiosqlite pydantic cryptography
```

**Ollama Connection Issues**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull required model
ollama pull llama3.2
```

**Permission Issues (Linux/Mac)**
```bash
chmod +x install.sh startup.py main.py
```

## 🎯 Usage

### First-Time Setup
When you run PersonaForge.AI for the first time, you'll be guided through setting up your professional profile:

1. **Basic Information**: Name, industry, experience level
2. **Current Work**: Role, company, main projects
3. **Skills to Showcase**: Key competencies you want to highlight
4. **Career Goals**: What you want to achieve through LinkedIn
5. **Content Preferences**: Tone, length, emoji usage
6. **Posting Strategy**: Frequency and timing preferences

### Main Features

#### 📝 Generate LinkedIn Posts
Choose from different post types:
- **Mini Project**: Quick wins, tools, or techniques learned
- **Main Project**: Significant work with detailed results
- **Capstone Project**: Major achievements and milestones
- **Industry Insight**: Thought leadership content
- **Achievement**: Milestone celebrations
- **General**: Professional updates

#### 📅 Schedule Content
- View upcoming posts in your content calendar
- Auto-schedule based on your strategy
- Manual scheduling with optimal time suggestions
- Analytics on posting performance

#### 📊 Analytics Dashboard
- Track engagement metrics and trends
- Analyze top-performing content themes
- Monitor posting schedule adherence
- Performance insights and recommendations

#### 📚 Content Library
- Browse all generated content (drafts, scheduled, posted)
- Organize posts by type and status
- Export content for external use

#### 🔒 Privacy Controls
- View current privacy settings
- Manage data encryption
- Clean up temporary files
- Export/backup your data

## 🏗️ Architecture

### Multi-Agent System
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Content       │    │   Image         │    │   Prompt        │
│   Agent         │    │   Agent         │    │   Agent         │
│                 │    │                 │    │                 │
│ • Post content  │    │ • Infographics  │    │ • Structured    │
│ • Hashtags      │    │ • Charts        │    │   prompts       │
│ • Engagement    │    │ • Quote images  │    │ • Optimization  │
│   prediction    │    │ • Process flow  │    │ • Consistency   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Agent         │
                    │   Coordinator   │
                    │                 │
                    │ • Orchestrates  │
                    │   all agents    │
                    │ • Manages flow  │
                    │ • Coordinates   │
                    │   generation    │
                    └─────────────────┘
```

### Data Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   Database      │    │   Privacy       │
│   Handler       │    │   Manager       │    │   Manager       │
│                 │    │                 │    │                 │
│ • Profile setup │    │ • SQLite DB     │    │ • Encryption    │
│ • Preferences   │    │ • Posts         │    │ • Local storage │
│ • Context       │    │ • Analytics     │    │ • Data cleanup  │
│   collection    │    │ • Schedules     │    │ • Privacy audit │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Content       │
                    │   Scheduler     │
                    │                 │
                    │ • Smart timing  │
                    │ • Auto posting  │
                    │ • Calendar mgmt │
                    │ • Strategy impl │
                    └─────────────────┘
```

## 📋 Configuration

### Environment Variables (.env)
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Database
DATABASE_PATH=data/linkedin_tool.db

# Privacy
LOCAL_STORAGE_ONLY=true
ENCRYPT_DATA=true

# Content
MAX_POST_LENGTH=3000
IMAGE_WIDTH=1200
IMAGE_HEIGHT=630
```

### User Configuration
The application maintains user-specific settings in `data/user_config.json`:
- User interface preferences
- Content generation settings
- Privacy and security options
- Scheduling preferences
- AI behavior settings

## 🔧 Advanced Features

### Custom Post Types
Extend the system with custom post types by modifying the agent configurations.

### Image Customization
The Image Agent supports multiple visual styles:
- Professional
- Corporate
- Modern
- Minimal
- LinkedIn-branded

### Analytics Integration
Track performance metrics:
- Engagement rates
- Best posting times
- Top-performing content themes
- Audience growth patterns

### Backup and Export
- Automatic settings backup
- Content library export
- Analytics data export
- Privacy-compliant data portability

## 🛡️ Security & Privacy

### Local-First Approach
- All data processing happens on your machine
- No external API calls for content generation
- No cloud storage dependencies
- Complete control over your data

### Encryption Options
- Optional data encryption using industry-standard methods
- Secure key management
- Encrypted storage for sensitive information
- Configurable encryption levels

### Data Management
- Automatic cleanup of temporary files
- Configurable data retention policies
- Secure deletion capabilities
- Privacy audit tools

## 🤝 Contributing

We welcome contributions! Please read our contributing guidelines and:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Ollama Connection Issues**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve
```

**Database Issues**
```bash
# Reset database (WARNING: This deletes all data)
rm data/linkedin_tool.db
python main.py  # Will recreate database
```

**Permission Issues**
```bash
# Fix file permissions
chmod 600 data/.encryption_key
chmod 755 data/
```

### Getting Help
- Check the troubleshooting section in the application
- Review system status in the main menu
- Check logs in `data/app.log`

## 🔄 Updates

The application includes built-in configuration management:
- Settings backup and restore
- Version migration
- Configuration validation
- Update notifications

## 🎯 Roadmap

- [ ] Web interface for easier management
- [ ] Advanced analytics dashboard
- [ ] LinkedIn API integration (optional)
- [ ] Team collaboration features
- [ ] Mobile companion app
- [ ] Advanced AI model support

---

**PersonaForge.AI** - Empowering professionals with privacy-focused LinkedIn automation.

*Built with ❤️ for the professional community*