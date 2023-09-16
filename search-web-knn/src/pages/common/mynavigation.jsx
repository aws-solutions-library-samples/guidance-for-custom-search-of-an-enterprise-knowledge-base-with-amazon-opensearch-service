import React from 'react';
import SideNavigation from '@cloudscape-design/components/side-navigation';

const navItems = [
    {
        type: "section",
        text: "Data Preparation",
        items: [
            {
                type: "link",
                text: "File Upload",
                href: "/file_upload"
            }
        ]
    },
    {
        type: "section",
        text: "Search Type",
        items: [
            {
                type: "link",
                text: "Search FAQ",
                href: "/"
            },
            {
                type: "link",
                text: "Search Doc",
                href: "/search_doc"
            },
            {
                type: "link",
                text: "Generate Report",
                href: "/gen_report"
            }

        ]
    },
    {
        type: "section",
        text: "Machine Learning",
        items: [
            {
                type: "link",
                text: "Training",
                href: "/ltr"
            }
        ]
    },
];

export function MyNavigation() {
    const [activeHref, setActiveHref] = React.useState(
        "#/Search"
    );
    return (
        <SideNavigation
            activeHref={activeHref}
            header={{text: "Smart Search Solution"}}
            items={navItems}
            onFollow={event => {
                if (!event.detail.external) {
                    // event.preventDefault();
                    setActiveHref(event.detail.href);
                }
            }}
        />
    );
}