import {
  Badge,
  Box,
  Button,
  Link,
  Modal,
  Popover,
  SpaceBetween,
  StatusIndicator,
  Table,
} from '@cloudscape-design/components';
import { useState } from 'react';
import styled from 'styled-components';

const TableSources = ({ sourceData }) => {
  return (
    <Table
      items={sourceData}
      loadingText="Loading resources"
      sortingDisabled
      variant="borderless"
      wrapLines
      // trackBy="id"
      empty={
        <Box margin={{ vertical: 'xs' }} textAlign="center" color="inherit">
          <SpaceBetween size="m">
            <b>No resources</b>
          </SpaceBetween>
        </Box>
      }
      columnDefinitions={[
        // {
        //   id: 'feedback',
        //   header: 'Feedback',
        //   isRowHeader: true,
        //   width: 90,
        //   cell: (item) => (
        //     <SpaceBetween direction="horizontal" size="xs">
        //       <ButtonFeedback id={item.id} isPositive />
        //       <ButtonFeedback id={item.id} />
        //     </SpaceBetween>
        //   ),
        // },
        {
          id: 'title',
          header: 'Title',
          isRowHeader: true,
          width: 200,
          cell: (item) =>
            item.titleLink ? (
              <Link href={item.titleLink}>{item.title || '-'}</Link>
            ) : (
              <span>{item.title || '-'}</span>
            ),
        },
        {
          id: 'scores',
          header: 'Scores',
          width: 120,
          cell: ({ scoreQueryDoc, scoreAnswerDoc }) => (
            <SpaceBetween direction="horizontal" size="xs">
              <Badge color="blue">
                QD: {scoreQueryDoc ? Number(scoreQueryDoc).toFixed(3) : 'n/a'}
              </Badge>
              <Badge color="blue">
                AD: {scoreAnswerDoc ? Number(scoreAnswerDoc).toFixed(3) : 'n/a'}
              </Badge>
            </SpaceBetween>
          ),
        },
        {
          id: 'paragraph',
          header: 'Paragraph',
          cell: (item) => (
            <div>
              <p>{item.paragraph || '-'}</p>
            </div>
          ),
        },
        {
          id: 'image',
          header: 'Image',
          width: 120,
          cell: ({ image }) => <SourceImage image={image} />,
        },
      ]}
    />
  );
};

export default TableSources;

function ButtonFeedback({ id, isPositive = false }) {
  return (
    <Popover
      dismissButton={false}
      position="top"
      size="small"
      triggerType="custom"
      content={
        <StatusIndicator type="success">Feedback collected</StatusIndicator>
      }
    >
      <Button
        iconName={isPositive ? 'thumbs-up-filled' : 'thumbs-down'}
        variant="icon"
        onClick={() => console.info(id)}
      />
    </Popover>
  );
}

const SourceImage = ({ image }) => {
  const [visible, setVisible] = useState(false);
  if (!image) return 'n/a';
  const src = image.startsWith('data:image')
    ? image
    : `data:image/png;base64,${image}`;
  return (
    <>
      <StyledImage
        src={src}
        alt="Source img"
        width="100%"
        height="auto"
        onClick={() => setVisible(true)}
      />
      <Modal visible={visible} onDismiss={() => setVisible(false)} size="max">
        <img src={src} alt="Source img" width="100%" height="auto" />
      </Modal>
    </>
  );
};
const StyledImage = styled.img`
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  &:hover {
    transform: scale(1.1);
  }
`;
