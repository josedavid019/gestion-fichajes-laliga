import {
  Camera,
  Brain,
  FileBarChart,
  Zap,
  TrendingUp,
  Users,
  Settings,
  FileText,
} from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  useSidebar,
} from "@/components/ui/sidebar";

const modules = [
  { title: "Dashboard", url: "/", icon: FileBarChart },
  { title: "Detección YOLO", url: "/detection", icon: Camera },
  { title: "Consulta IA / RAG", url: "/ai-query", icon: Brain },
  { title: "Predicciones", url: "/prediction", icon: TrendingUp },
  { title: "Gestión de Jugadores", url: "/scouting", icon: Users },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();
  const { user } = useAuth();

  // Check if user is admin
  const isAdmin =
    user?.email === "admin@example.com" || (user as any)?.is_staff === true;

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-4 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <Zap className="w-4 h-4 text-primary" />
          </div>
          {!collapsed && (
            <div>
              <h2 className="font-heading text-sm font-bold text-foreground">
                ScoutAI
              </h2>
              <p className="text-[10px] text-muted-foreground">
                Football Intelligence
              </p>
            </div>
          )}
        </div>
      </SidebarHeader>
      <SidebarContent className="pt-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {modules.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className="hover:bg-muted/50 transition-colors"
                      activeClassName="bg-primary/10 text-primary font-medium border-l-2 border-primary"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && (
                        <span className="text-sm">{item.title}</span>
                      )}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}

              {/* Admin Section */}
              {isAdmin && (
                <>
                  <SidebarMenuItem key="admin-divider" className="my-2">
                    <div className="border-t border-border/30" />
                  </SidebarMenuItem>
                  <SidebarMenuItem key="admin-label">
                    {!collapsed && (
                      <p className="text-xs font-semibold text-muted-foreground px-2 py-2 uppercase">
                        Administración
                      </p>
                    )}
                  </SidebarMenuItem>
                  <SidebarMenuItem key="users-management">
                    <SidebarMenuButton asChild>
                      <NavLink
                        to="/admin/users"
                        className="hover:bg-muted/50 transition-colors"
                        activeClassName="bg-primary/10 text-primary font-medium border-l-2 border-primary"
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        {!collapsed && (
                          <span className="text-sm">Gestión de Usuarios</span>
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem key="audit-logs">
                    <SidebarMenuButton asChild>
                      <NavLink
                        to="/admin/audit-logs"
                        className="hover:bg-muted/50 transition-colors"
                        activeClassName="bg-primary/10 text-primary font-medium border-l-2 border-primary"
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        {!collapsed && (
                          <span className="text-sm">Logs de Auditoría</span>
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </>
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
