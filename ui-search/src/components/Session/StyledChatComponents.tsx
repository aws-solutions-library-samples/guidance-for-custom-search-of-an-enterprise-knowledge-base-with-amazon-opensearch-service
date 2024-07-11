import * as awsui from '@cloudscape-design/design-tokens';
import { styled } from 'styled-components';

export const StyledQ = styled.div`
  display: flex;
  align-items: start;
  gap: ${awsui.spaceScaledS};
  padding: 10px;

  .icon {
    padding-top: 3px;
    width: ${awsui.spaceScaledL};
  }
  .text {
    /* width: 100%; */
    flex: 1;
  }
  .extra {
    width: 180px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: ${awsui.spaceScaledXxs};
  }
`;

export const StyledAContainer = styled(StyledQ)`
  display: block;
  background-color: ${awsui.colorBackgroundCellShaded};
  border-radius: ${awsui.borderRadiusAlert};
  padding: 0;

  .expandable {
    padding: 0 ${awsui.spaceScaledXxl};
    /* padding: 0 ${awsui.spaceScaledXs} 0 ${awsui.spaceScaledXxl}; */
    min-height: 10px;
    .display-source {
    }
  }
`;
