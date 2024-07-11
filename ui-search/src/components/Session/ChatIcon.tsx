import { Icon, IconProps } from '@cloudscape-design/components';
import { StyledBoxVerticalCenter } from '../StyledComponents';
import React from 'react';

const ChatIcon: React.FC<{ name?: IconProps.Name }> = ({
  name = 'user-profile',
}) => {
  return (
    <StyledBoxVerticalCenter>
      <Icon name={name} />
    </StyledBoxVerticalCenter>
  );
};

export default ChatIcon;
