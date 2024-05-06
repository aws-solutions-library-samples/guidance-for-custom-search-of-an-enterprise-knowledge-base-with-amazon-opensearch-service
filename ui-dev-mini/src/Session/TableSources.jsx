import {
  Badge,
  Box,
  Link,
  SpaceBetween,
  Table,
} from '@cloudscape-design/components'

const TableSources = ({ sourceData }) => {
  return (
    <Table
      items={sourceData}
      loadingText='Loading resources'
      sortingDisabled
      variant='borderless'
      wrapLines
      // trackBy="id"
      empty={
        <Box margin={{ vertical: 'xs' }} textAlign='center' color='inherit'>
          <SpaceBetween size='m'>
            <b>No resources</b>
          </SpaceBetween>
        </Box>
      }
      columnDefinitions={[
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
            <SpaceBetween direction='horizontal' size='xs'>
              <Badge color='blue'>
                QD: {scoreQueryDoc ? Number(scoreQueryDoc).toFixed(3) : 'n/a'}
              </Badge>
              <Badge color='blue'>
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
      ]}
    />
  )
}

export default TableSources
