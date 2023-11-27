import { Icon } from '@cloudscape-design/components';
import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="custom-main-footer" id="f">
      <ul>
        <li>
          <Link to="/about">About</Link>
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
