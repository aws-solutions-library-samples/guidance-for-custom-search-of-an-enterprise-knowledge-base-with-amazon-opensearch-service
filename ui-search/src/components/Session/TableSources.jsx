import {
  Badge,
  Box,
  Button,
  Link,
  Popover,
  SpaceBetween,
  StatusIndicator,
  Table,
} from '@cloudscape-design/components';

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
                QD: {scoreQueryDoc ? Number(scoreQueryDoc).toFixed(4) : 'n/a'}
              </Badge>
              <Badge color="blue">
                AD: {scoreAnswerDoc ? Number(scoreAnswerDoc).toFixed(4) : 'n/a'}
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
        onClick={() => console.log(id)}
      />
    </Popover>
  );
}
