import { Icon } from '@cloudscape-design/components';
import { StyledBoxVerticalCenter } from '../StyledComponents';

const ChatIcon = ({ name = 'user-profile' }) => {
  return (
    <StyledBoxVerticalCenter>
      <Icon name={name} />
    </StyledBoxVerticalCenter>
  );
};

export default ChatIcon;
