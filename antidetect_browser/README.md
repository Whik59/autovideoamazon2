# Custom Anti-Detect Browser

A privacy-focused browser with advanced fingerprint spoofing and proxy support, designed for manual Google/YouTube account creation and management.

## Features

🔒 **Advanced Fingerprint Spoofing**
- Canvas fingerprint randomization
- WebGL parameter spoofing
- Screen resolution spoofing
- User agent randomization
- Hardware fingerprint masking
- Timezone spoofing

🌐 **Proxy Support**
- ISP proxy integration
- HTTP/HTTPS proxy support
- Per-profile proxy configuration
- Proxy testing functionality

👤 **Profile Management**
- Isolated browser profiles
- Persistent storage per profile
- Cookie and session isolation
- Profile-specific fingerprints

🎯 **Google Account Creation Optimized**
- Quick access to Gmail, YouTube, Google
- Manual account creation workflow
- OAuth token extraction ready
- Multi-channel management support

## Installation

1. **Install Python Dependencies:**
```bash
cd antidetect_browser
pip install -r requirements.txt
```

2. **Install System Dependencies:**

**Windows:**
- Download and install Visual C++ Redistributable
- PyQt5 should work out of the box

**Linux:**
```bash
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine
```

**macOS:**
```bash
brew install pyqt5
```

## Quick Start

1. **Launch the Browser:**
```bash
python main.py
```

2. **Create Your First Profile:**
   - Click "New Profile" in the sidebar
   - Enter a profile name (e.g., "Account_001")
   - Configure your ISP proxy settings:
     - Host: `gw.thunderproxy.net`
     - Port: `5959`
     - Username: `0veAOAHVmW1Cdh12Ug-stc-isp-sid-0`
     - Password: `MjoYlZPyVLz16Jv`
   - Click "Test Proxy" to verify connection
   - Save the profile

3. **Open a Browser Tab:**
   - Click "+ New Tab"
   - Select your profile
   - Start browsing with your unique fingerprint!

## Usage Workflow

### Creating Google Accounts

1. **Create Profile:** One profile = One Google account
2. **Open Tab:** Select the profile for your new account
3. **Navigate:** Use quick buttons or manually go to:
   - Gmail: `https://gmail.com`
   - Google: `https://accounts.google.com`
4. **Manual Creation:** Follow Google's signup process normally
5. **Verify:** Use SMS verification services as needed
6. **Create Channels:** Go to YouTube and create 2 channels per account

### Profile Management

**One Profile = One Identity**
- Each profile has a unique fingerprint
- Separate cookies, cache, and storage
- Dedicated proxy configuration
- Persistent across sessions

**Best Practices:**
- Use descriptive names: `Account_001`, `Channel_Gaming_001`
- One proxy per profile for maximum isolation
- Test proxy before creating accounts
- Keep profiles organized by purpose

## Proxy Configuration

### ISP Proxy Format
```
Host: gw.thunderproxy.net
Port: 5959
Username: 0veAOAHVmW1Cdh12Ug-stc-isp-sid-0
Password: MjoYlZPyVLz16Jv
```

### Multiple Proxies
For scaling, configure different proxies per profile:
- `Account_001` → Proxy_1
- `Account_002` → Proxy_2
- `Account_003` → Proxy_3

## Fingerprint Spoofing

Each profile automatically generates:
- **Unique User Agent:** Recent Chrome versions
- **Screen Resolution:** Common resolutions (1920x1080, 1366x768, etc.)
- **Platform:** Windows, macOS, or Linux
- **Hardware:** CPU cores, RAM, touch points
- **Canvas Noise:** Randomized canvas fingerprint
- **WebGL Parameters:** GPU vendor/renderer spoofing
- **Timezone:** Random timezone offset

## Directory Structure

```
antidetect_browser/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── profiles/           # Created automatically
    ├── Account_001/
    │   ├── config.json
    │   ├── cache/
    │   └── storage/
    └── Account_002/
        ├── config.json
        ├── cache/
        └── storage/
```

## Integration with YouTube Pipeline

After creating accounts manually:

1. **Extract OAuth Tokens:** Use browser dev tools or automation
2. **Save Credentials:** Store in your `credentials/` folder
3. **Update Pipeline:** Add new `client.json` files
4. **Upload Videos:** Use your existing `run_pipeline.py`

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install --upgrade PyQt5 PyQtWebEngine
```

**Proxy connection fails:**
- Verify proxy credentials
- Check firewall settings
- Try different proxy endpoint

**Browser crashes:**
- Update graphics drivers
- Disable hardware acceleration
- Check system resources

**Fingerprint not working:**
- Clear browser cache
- Create new profile
- Restart application

### Debug Mode

Enable debug output:
```bash
python main.py --debug
```

## Security Notes

🔒 **Privacy Features:**
- No telemetry or tracking
- Local storage only
- Encrypted profile storage
- Secure proxy handling

⚠️ **Important:**
- Use high-quality ISP proxies
- Don't reuse proxies across profiles
- Keep profiles isolated
- Regular proxy rotation recommended

## Advanced Configuration

### Custom Fingerprints

Edit `BrowserProfile.generate_fingerprint()` to customize:
- User agent patterns
- Screen resolution pools
- Hardware specifications
- Geographic preferences

### Proxy Providers

Tested with:
- ThunderProxy (ISP)
- Bright Data (Residential)
- Oxylabs (ISP)
- SmartProxy (Residential)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review proxy configuration
3. Test with a simple profile first
4. Verify system dependencies

## License

This software is for educational and legitimate business purposes only. Users are responsible for complying with all applicable laws and terms of service. 