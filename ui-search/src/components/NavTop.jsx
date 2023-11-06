import { TopNavigation } from '@cloudscape-design/components';
import {
  applyDensity,
  applyMode,
  Density,
  Mode,
} from '@cloudscape-design/global-styles';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useLsAppConfigs from 'src/hooks/useLsAppConfigs';

const i18nStrings = {
  searchIconAriaLabel: 'Search',
  searchDismissIconAriaLabel: 'Close search',
  overflowMenuTriggerText: 'More',
  overflowMenuTitleText: 'All',
  overflowMenuBackIconAriaLabel: 'Back',
  overflowMenuDismissIconAriaLabel: 'Close menu',
};

const profileActions = [
  { type: 'button', id: 'profile', text: 'Profile' },
  { type: 'button', id: 'preferences', text: 'Preferences' },
  { type: 'button', id: 'security', text: 'Security' },
  {
    type: 'menu-dropdown',
    id: 'support-group',
    text: 'Support',
    items: [
      {
        id: 'documentation',
        text: 'Documentation',
        href: '#',
        external: true,
        externalIconAriaLabel: ' (opens in new tab)',
      },
      {
        id: 'feedback',
        text: 'Feedback',
        href: '#',
        external: true,
        externalIconAriaLabel: ' (opens in new tab)',
      },
      { id: 'support', text: 'Customer support' },
    ],
  },
  { type: 'button', id: 'signout', text: 'Sign out' },
];

export default function TopNav() {
  const { appConfigs, setAConfig } = useLsAppConfigs();
  const [themeBool, setThemeBool] = useState(appConfigs.mode !== 'light');
  const [spacingBool, setSpacingBool] = useState(
    appConfigs.density !== 'comfortable'
  );

  useEffect(() => {
    setThemeBool(appConfigs.mode !== 'light');
    setSpacingBool(appConfigs.density !== 'comfortable');
  }, [appConfigs.density, appConfigs.mode]);

  const navigate = useNavigate();
  return (
    <TopNavigation
      i18nStrings={i18nStrings}
      identity={{
        href: '/',
        title:
          'Guidance for Custom Search of an Enterprise Knowledge Base on AWS',
        // title: 'Smart Search Solution',
        // logo: { src: logo, alt: 'Service name logo' },
      }}
      utilities={[
        {
          type: 'button',
          iconName: themeBool ? 'star-filled' : 'star',
          // text: themeBool ? 'bright' : 'dark',
          ariaLabel: 'ThemeSwitch',
          // disableUtilityCollapse: true,
          onClick: () => {
            setThemeBool((prev) => !prev);
            const bool = appConfigs.mode === 'light';
            setAConfig('mode', bool ? 'dark' : 'light');
            applyMode(bool ? Mode.Dark : Mode.Light);
          },
        },
        {
          type: 'button',
          iconName: spacingBool ? 'view-full' : 'zoom-to-fit',
          // text: themeBool ? 'bright' : 'dark',
          ariaLabel: 'SpacingSwitch',
          // disableUtilityCollapse: true,
          onClick: () => {
            setSpacingBool((prev) => !prev);
            const bool = appConfigs.density === 'comfortable';
            setAConfig('density', bool ? 'compact' : 'comfortable');
            applyDensity(bool ? Density.Compact : Density.Comfortable);
          },
        },
        // {
        //   type: 'button',
        //   iconName: 'notification',
        //   ariaLabel: 'Notifications',
        //   badge: true,
        //   disableUtilityCollapse: true,
        // },
        {
          type: 'button',
          iconName: 'settings',
          title: 'Settings',
          ariaLabel: 'Settings',
          onClick: () => {
            navigate('/app-configs');
          },
        },
        {
          type: 'menu-dropdown',
          text: 'Customer Name',
          description: 'customer@example.com',
          iconName: 'user-profile',
          items: profileActions,
        },
      ]}
    />
  );
}
