import { Box } from '@cloudscape-design/components';
import * as awsui from '@cloudscape-design/design-tokens';
import styled from 'styled-components';

export const StyledBoxVerticalCenter = styled(Box)`
  /* color: ${awsui.colorTextBodySecondary}; */
  /* border: 2px ${awsui.colorBorderInputDefault} solid;
  border-spacing: 0;
  border-radius: 18px; */
  /* height: calc(${awsui.spaceScaledXxl} - 4px); */
  height: 100%;
  width: 100%;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  > div {
    flex: 1;
  }
`;
