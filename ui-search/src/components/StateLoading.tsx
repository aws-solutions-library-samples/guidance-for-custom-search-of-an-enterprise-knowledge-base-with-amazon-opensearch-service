import {
  Box,
  Container,
  Header,
  Spinner,
  SpinnerProps,
} from '@cloudscape-design/components';
import React from 'react';

const StateLoading = ({
  size = 'big',
  headerText = '',
}: {
  size?: SpinnerProps.Size;
  headerText?: string;
}) => {
  return (
    <Container
      header={
        !headerText ? null : (
          <Header variant="h3">
            <span style={{ fontWeight: 200 }}>{headerText}</span>
          </Header>
        )
      }
    >
      <Box textAlign="center" margin="l">
        <Spinner size={size} />
      </Box>
    </Container>
  );
};

export default StateLoading;
