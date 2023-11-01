import { Box, Container, Header, Spinner } from '@cloudscape-design/components';
import React from 'react';

const StateLoading = ({ size = 'big', headerText = '' }) => {
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
