// project-imports
import { NavActionType } from 'config';

// material-ui icons
import {
  Add,
  Link,
  Apps,
  Message,
  CalendarToday,
  ViewKanban,
  People,
  Receipt,
  Person,
  ShoppingBag,
  CloudUpload
} from '@mui/icons-material';

// assets
// Removed iconsax-react imports as we're using Material-UI icons

// types
import { NavItemType } from 'types/menu';

// icons
const icons = {
  applications: Apps,
  chat: Message,
  calendar: CalendarToday,
  kanban: ViewKanban,
  customer: People,
  invoice: Receipt,
  profile: Person,
  ecommerce: ShoppingBag,
  add: Add,
  link: Link,
  upload: CloudUpload
};

// ==============================|| MENU ITEMS - APPLICATIONS ||============================== //

const applications: NavItemType = {
  id: 'group-applications',
  title: 'applications',
  icon: icons.applications,
  type: 'group',
  children: [
    {
      id: 'chat',
      title: 'chat',
      type: 'item',
      url: '/apps/chat',
      icon: icons.chat,
      breadcrumbs: false
    },
    {
      id: 'file-upload',
      title: 'Upload',
      type: 'item',
      url: '/file-upload',
      icon: icons.upload,
      breadcrumbs: false
    },
    {
      id: 'calendar',
      title: 'calendar',
      type: 'item',
      url: '/apps/calendar',
      icon: icons.calendar,
      actions: [
        {
          type: NavActionType.LINK,
          label: 'Full Calendar',
          icon: icons.link,
          url: 'https://fullcalendar.io/docs/react',
          target: true
        }
      ]
    },
    {
      id: 'kanban',
      title: 'kanban',
      type: 'item',
      url: '/apps/kanban/board',
      icon: icons.kanban,
      breadcrumbs: false
    },
    {
      id: 'invoice',
      title: 'invoice',
      url: '/apps/invoice/dashboard',
      type: 'collapse',
      icon: icons.invoice,
      breadcrumbs: false,
      children: [
        {
          id: 'invoice-create',
          title: 'create',
          type: 'item',
          url: '/apps/invoice/create',
          breadcrumbs: false
        },
        {
          id: 'invoice-details',
          title: 'details',
          type: 'item',
          url: '/apps/invoice/details/1',
          breadcrumbs: false
        },
        {
          id: 'invoice-list',
          title: 'list',
          type: 'item',
          url: '/apps/invoice/list',
          breadcrumbs: false
        },
        {
          id: 'invoice-edit',
          title: 'edit',
          type: 'item',
          url: '/apps/invoice/edit/1',
          breadcrumbs: false
        }
      ]
    },
    {
      id: 'profile',
      title: 'profile',
      type: 'collapse',
      icon: icons.profile,
      children: [
        {
          id: 'user-profile',
          title: 'user-profile',
          type: 'item',
          url: '/apps/profiles/user/personal',
          breadcrumbs: false
        },
        {
          id: 'account-profile',
          title: 'account-profile',
          type: 'item',
          url: '/apps/profiles/account/basic',
          breadcrumbs: false
        }
      ]
    },

    {
      id: 'e-commerce',
      title: 'e-commerce',
      type: 'collapse',
      icon: icons.ecommerce,
      children: [
        {
          id: 'products',
          title: 'products',
          type: 'item',
          url: '/apps/e-commerce/products'
        },
        {
          id: 'product-details',
          title: 'product-details',
          type: 'item',
          url: '/apps/e-commerce/product-details/1',
          breadcrumbs: false
        },
        {
          id: 'product-list',
          title: 'product-list',
          type: 'item',
          url: '/apps/e-commerce/product-list'
        },
        {
          id: 'add-new-product',
          title: 'add-new-product',
          type: 'item',
          url: '/apps/e-commerce/add-new-product'
        },
        {
          id: 'checkout',
          title: 'checkout',
          type: 'item',
          url: '/apps/e-commerce/checkout'
        }
      ]
    }
  ]
};

export default applications;
