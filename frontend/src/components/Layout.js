import React, { useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AuthContext } from "@/App";
import { Button } from "@/components/ui/button";
import { Server, HardDrive, Users, Settings, LogOut, LayoutDashboard } from "lucide-react";

const Layout = ({ children }) => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard, testId: "nav-dashboard" },
    { name: "Servers", path: "/servers", icon: Server, testId: "nav-servers" },
    { name: "Nodes", path: "/nodes", icon: HardDrive, testId: "nav-nodes" },
    { name: "Users", path: "/users", icon: Users, testId: "nav-users", adminOnly: true },
    { name: "Settings", path: "/settings", icon: Settings, testId: "nav-settings" },
  ];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 glass border-r border-slate-700 p-6 flex flex-col" data-testid="sidebar">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg">
              <Server className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">ServerCraft</h1>
          </div>
          <p className="text-sm text-slate-400 ml-11">Game Server Panel</p>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map((item) => {
            if (item.adminOnly && user?.role !== "admin") return null;
            
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <button
                key={item.path}
                data-testid={item.testId}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
                    : "text-slate-300 hover:bg-slate-700/50"
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="border-t border-slate-700 pt-4 space-y-3">
          <div className="px-4 py-2">
            <p className="text-sm text-slate-400">Logged in as</p>
            <p className="text-white font-medium">{user?.username}</p>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
          <Button
            data-testid="logout-button"
            onClick={handleLogout}
            variant="ghost"
            className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-500/10"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;