// project-imports
import adminPanel from './admin-panel';
import applications from './applications';
import widget from './widget';
import formsTables from './forms-tables';
import samplePage from './sample-page';
import chartsMap from './charts-map';
import pages from './pages';

// types
import { NavItemType } from 'types/menu';

// ==============================|| MENU ITEMS ||============================== //

const menuItems: { items: NavItemType[] } = {
  items: [widget, adminPanel, applications, formsTables, chartsMap, samplePage, pages]
};

export default menuItems;
