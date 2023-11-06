import {
  Box,
  Button,
  ColumnLayout,
  Container,
  Header,
  Popover,
  SpaceBetween,
  StatusIndicator,
} from '@cloudscape-design/components';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionStore } from 'src/stores/session';
import StateLoading from '../StateLoading';
import ValueWithLabel from '../ValueWithLabel';

const SIZE = 'l';
const SessionBrief = ({ configs, expanded }) => {
  const { delSession } = useSessionStore((s) => [s.delSession]);
  const navigate = useNavigate();
  const [displayDetails, setDisplayDetails] = useState(true);

  if (!configs) return <StateLoading headerText="Loading Session Configs..." />;

  const {
    name,
    searchEngine,
    llmData,
    role,
    language,
    taskDefinition,
    outputFormat,
    isCheckedGenerateReport,
    isCheckedContext,
    isCheckedKnowledgeBase,
    isCheckedMapReduce,
    indexName,
    topK,
    isCheckedScoreQA,
    isCheckedScoreQD,
    isCheckedScoreAD,
    sessionId,
    prompt,
  } = configs;

  return (
    <Container
      header={
        <Header
          variant="h3"
          actions={
            <SpaceBetween direction="horizontal" size="xxl">
              <Button onClick={() => setDisplayDetails((prev) => !prev)}>
                {displayDetails ? 'Hide' : 'Show'} Session Details
              </Button>
              <Button
                iconName="remove"
                variant="primary"
                onClick={() => {
                  const bool = confirm(
                    '‼️ Confirm to delete this session. This operation is irreversible!'
                  );
                  if (bool) {
                    delSession(sessionId);
                    navigate('/');
                  }
                }}
              />
            </SpaceBetween>
          }
        >
          <span>{name} </span>
          <h5 style={{ display: 'inline', fontWeight: 400 }}>
            <span>- ID {sessionId} </span>
            <Box margin={{ right: 'xxs' }} display="inline-block">
              <Popover
                size="small"
                position="top"
                dismissButton={false}
                triggerType="custom"
                content={
                  <StatusIndicator type="success">
                    Session ID copied
                  </StatusIndicator>
                }
              >
                <Button
                  variant="inline-icon"
                  iconName="copy"
                  ariaLabel="Copy ARN"
                  onClick={() => navigator.clipboard.writeText(sessionId)}
                />
              </Popover>
            </Box>
          </h5>
        </Header>
      }
    >
      {!displayDetails ? null : (
        <ColumnLayout columns={4} variant="text-grid">
          <SpaceBetween size={SIZE}>
            <ValueWithLabel label="Engine">{searchEngine}</ValueWithLabel>
            <ValueWithLabel label="Language Model">
              {llmData?.modelName}
            </ValueWithLabel>
            <ValueWithLabel label="Index Name">{indexName}</ValueWithLabel>
          </SpaceBetween>

          <SpaceBetween size={SIZE}>
            {/* <ValueWithLabel label="Role">{role}</ValueWithLabel> */}
            <ValueWithLabel label="Language">{language}</ValueWithLabel>
            <ValueWithLabel label="Top K">Top {topK}</ValueWithLabel>
          </SpaceBetween>

          <SpaceBetween size={SIZE}>
            {/* <ValueWithLabel label="Output Format">
              {outputFormat}
            </ValueWithLabel>
            <ValueWithLabel label="Task Definition">
              {taskDefinition}
            </ValueWithLabel> */}
            <ValueWithLabel label="Prompt">
              <p style={{ marginTop: 0 }}>{prompt}</p>
            </ValueWithLabel>
          </SpaceBetween>

          <SpaceBetween size="xs">
            <BoolState bool={isCheckedGenerateReport} text="Generate Report" />
            <BoolState bool={isCheckedContext} text="Context" />
            <BoolState bool={isCheckedKnowledgeBase} text="Knowledge Base" />
            <BoolState bool={isCheckedMapReduce} text="Map Reduce" />
            <BoolState bool={isCheckedScoreQA} text="Score Question-Answer" />
            <BoolState bool={isCheckedScoreQD} text="Score Question-Doc" />
            <BoolState bool={isCheckedScoreAD} text="Score Answer-Doc" />
          </SpaceBetween>
        </ColumnLayout>
      )}
    </Container>
  );
};

export default SessionBrief;

function BoolState({ bool, text }) {
  return (
    <StatusIndicator type={bool ? 'success' : 'stopped'}>
      {text}
    </StatusIndicator>
  );
}
