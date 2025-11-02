# ServerCraft - Game Server Management Panel

A modern, sleek, and automated game server management panel with full Docker support for managing multiple game servers across different nodes.

## 🚀 Features

### Core Features
- **Multi-Node Support** - Manage servers across multiple infrastructure nodes
- **Docker Container Management** - Automated game server deployment using Docker
- **JWT Authentication** - Secure token-based authentication system
- **Sub-User Management** - Granular permission system for team access
- **File Explorer** - Browse and manage server files
- **Arma 3 Workshop Integration** - Upload .html mod lists and auto-download Steam Workshop mods
- **Server Selling** - Optional feature to sell servers to friends/community

### Supported Games (Initial Release)
- Arma 3 (Vanilla & Modded)
- Rust (Vanilla)
- Arma Reforger
- DayZ
- ICARUS
- Escape from Tarkov SPT
- Ground Branch
- Operation Harsh Doorstop
- Squad

## 🛠️ Technology Stack

**Backend:** FastAPI, MongoDB, Motor, Docker SDK, JWT, BeautifulSoup4  
**Frontend:** React 19, TailwindCSS, Shadcn/UI, Axios, React Router

## 🎯 Quick Start

### Using the Panel

1. **Register**: Create an admin account at `/login`
2. **Add a Node**: Go to Nodes page and add your first server node
3. **Create Server**: Navigate to Servers and create a game server
4. **Manage**: Start/Stop/Restart servers with one click

### Test Credentials
- Email: `admin@servercraft.com`
- Password: `Admin123!`

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login

### Servers
- `GET /api/servers` - List servers
- `POST /api/servers` - Create server
- `POST /api/servers/{id}/start` - Start
- `POST /api/servers/{id}/stop` - Stop
- `POST /api/servers/{id}/restart` - Restart

### Nodes
- `GET /api/nodes` - List nodes
- `POST /api/nodes` - Create node
- `PUT /api/nodes/{id}` - Update node

### File Management
- `GET /api/servers/{id}/files` - Browse files
- `POST /api/servers/{id}/files/upload` - Upload file

## 🎨 UI Highlights

- Modern glassmorphism design
- Dark theme with cyan/blue gradient accents
- Real-time status indicators
- Smooth animations
- Fully responsive layout

## 🔒 Security

- Bcrypt password hashing
- JWT authentication
- Role-based permissions
- CORS configuration

## 📦 Docker Compose Deployment

```yaml
version: '3.8'
services:
  servercraft:
    image: servercraft-panel:latest
    ports:
      - "3000:3000"
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - JWT_SECRET_KEY=your-secret-key
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - mongo
  mongo:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db
volumes:
  mongo-data:
```

## 📝 Future Enhancements

- Real-time console output
- Automated backups
- Email notifications
- Payment gateway integration
- More game support
- Advanced monitoring
- Server templates

---

**Note**: This is a full-featured game server management panel. Docker must be available for server deployment features to work.
