// assets
import { AdminPanelSettings, Dashboard, People, Support, Analytics, Description, History, BugReport, Message, Upload } from '@mui/icons-material';

// types
import { NavItemType } from 'types/menu';

// ==============================|| MENU ITEMS - ADMIN PANEL ||============================== //

const adminPanel: NavItemType = {
  id: 'admin-panel',
  title: 'Admin Panel',
  type: 'group',
  icon: AdminPanelSettings,
  children: [
    {
      id: 'admin-dashboard',
      title: 'Dashboard',
      type: 'item',
      url: '/admin/dashboard',
      icon: Dashboard,
      breadcrumbs: false
    },
    {
      id: 'users',
      title: 'Users',
      type: 'item',
      url: '/admin/users',
      icon: People,
      breadcrumbs: false
    },
    {
      id: 'admin-file-upload',
      title: 'File Upload',
      type: 'item',
      url: '/admin/file-upload',
      icon: Upload,
      breadcrumbs: false
    },
    {
      id: 'admin-scraping',
      title: 'Scraping Management',
      type: 'item',
      url: '/admin/scraping',
      icon: BugReport,
      breadcrumbs: false
    },
    {
      id: 'reports',
      title: 'Reports',
      type: 'item',
      url: '/admin/reports',
      icon: Analytics,
      breadcrumbs: false
    },
    {
      id: 'admin-messages',
      title: 'Messages',
      type: 'item',
      url: '/admin/messages',
      icon: Message,
      breadcrumbs: false
    },
    {
      id: 'admin-history',
      title: 'File History',
      type: 'item',
      url: '/admin/history',
      icon: History,
      breadcrumbs: false
    }
  ]
};

export default adminPanel;
