import { Icon } from '@cloudscape-design/components';
import React from 'react';

const Footer = () => {
  return (
    <footer className="custom-main-footer" id="f">
      <ul>
        <li>
          <a href="/about/about-cloudscape/">About</a>
        </li>
        <li>
          <a href="/about/connect/">Connect</a>
        </li>
        <li>
          <a
            href="https://aws.amazon.com/privacy/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Privacy
            <Icon name="external" />
          </a>
        </li>
        <li>
          <a
            href="https://aws.amazon.com/terms/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Site terms
            <Icon name="external" />
          </a>
        </li>
        <li>
          © 2023, Amazon Web Services, Inc. or its affiliates. All rights
          reserved.
        </li>
      </ul>
      <div className="made-with-love">
        <span>Made with love at Amazon</span>
      </div>
    </footer>
  );
};

export default Footer;
