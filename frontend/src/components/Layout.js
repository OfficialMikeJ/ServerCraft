import React, { useContext } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { AuthContext } from "@/App";
import { useTheme } from "@/themes/ThemeContext";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Server, HardDrive, Users, Settings, LogOut, LayoutDashboard, Palette } from "lucide-react";

const Layout = ({ children }) => {
  const { user, logout } = useContext(AuthContext);
  const { theme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard, testId: "nav-dashboard" },
    { name: "Servers", path: "/servers", icon: Server, testId: "nav-servers" },
    { name: "Nodes", path: "/nodes", icon: HardDrive, testId: "nav-nodes" },
    { name: "Users", path: "/users", icon: Users, testId: "nav-users", adminOnly: true },
    { name: "Themes & Plugins", path: "/themes-plugins", icon: Palette, testId: "nav-themes-plugins", adminOnly: true, disabled: true },
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
            <div 
              className="p-2 rounded-lg"
              style={{
                background: theme.gradient,
                boxShadow: `0 4px 12px ${theme.shadow}`
              }}
            >
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
            
            if (item.disabled) {
              return (
                <TooltipProvider key={item.path}>
                  <Tooltip delayDuration={0}>
                    <TooltipTrigger asChild>
                      <button
                        data-testid={item.testId}
                        disabled
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition text-slate-500 cursor-not-allowed opacity-50"
                      >
                        <Icon className="w-5 h-5" />
                        <span className="font-medium">{item.name}</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="bg-slate-800 border-slate-700 p-4 max-w-xs">
                      <p className="text-center text-slate-200 leading-relaxed">
                        This feature is still in development. Please allow me some time to finish this and test it internally. Once I have done my testing it will be fully released.
                        <br />
                        <span className="text-cyan-400 font-medium">- Mike</span>
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              );
            }
            
            return (
              <button
                key={item.path}
                data-testid={item.testId}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition themed-button ${
                  isActive ? "nav-item-active" : ""
                }`}
                style={
                  isActive
                    ? {
                        background: theme.gradient,
                        border: `2px solid ${theme.borderAccent}`,
                        boxShadow: `0 4px 12px ${theme.shadow}`,
                        color: "#ffffff",
                      }
                    : {
                        color: theme.textSecondary,
                        border: "2px solid transparent",
                      }
                }
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