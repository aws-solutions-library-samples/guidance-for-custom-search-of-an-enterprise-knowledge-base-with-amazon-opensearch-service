import {
  Box,
  Button,
  ColumnLayout,
  Grid,
  Container,
  Header,
  Popover,
  SpaceBetween,
  StatusIndicator,
  ExpandableSection,
} from '@cloudscape-design/components';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionStore } from 'src/stores/session';
import StateLoading from '../StateLoading';
import ValueWithLabel from '../ValueWithLabel';
import Divider from '../Divider';
import { DEFAULT_WORK_FLOW, DEFAULT_WORK_MODE } from 'src/constants';

const SIZE = 'l';
const SessionBrief = ({ configs }) => {
  const { delSession } = useSessionStore((s) => [s.delSession]);
  const navigate = useNavigate();
  const [displayDetails, setDisplayDetails] = useState(false);

  if (!configs) return <StateLoading headerText="Loading Session Configs..." />;

  const {
    name,
    searchEngine,
    llmData,
    workMode = DEFAULT_WORK_MODE,
    workFlow = DEFAULT_WORK_FLOW,
    chatSystemPrompt,
    role,
    language,
    taskDefinition,
    outputFormat,
    contextRounds,
    isCheckedGenerateReport,
    isCheckedContext,
    isCheckedKnowledgeBase,
    isCheckedMapReduce,
    indexName,
    kendraIndexId,
    topK,
    searchMethod,
    txtDocsNum,
    vecDocsScoreThresholds,
    txtDocsScoreThresholds,
    isCheckedScoreQA,
    isCheckedScoreQD,
    isCheckedScoreAD,
    sessionId,
    prompt,
    tokenContentCheck,
  } = configs;

  const isKendra = searchEngine === 'kendra';

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
                  const bool = window?.confirm(
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
        <Grid gridDefinition={[{ colspan: 3 }, { colspan: 6 }, { colspan: 3 }]}>
          <SpaceBetween size={SIZE}>
            <ValueWithLabel label="Engine">{searchEngine}</ValueWithLabel>
            <ValueWithLabel label="Work Mode">{workMode}</ValueWithLabel>
            <ValueWithLabel label="Language Model Strategy">
              {llmData?.strategyName}
            </ValueWithLabel>
            <ValueWithLabel label="Language">{language}</ValueWithLabel>
            {isKendra ? (
              <ValueWithLabel label="Kendra Index ID">
                {kendraIndexId}
              </ValueWithLabel>
            ) : (
              <ValueWithLabel label="Index Name">{indexName}</ValueWithLabel>
            )}
            {isKendra ? null : (
              <ValueWithLabel label="Search Method">
                {searchMethod}
              </ValueWithLabel>
            )}
            <ValueWithLabel label="Context Rounds">
              {contextRounds ?? 3}
            </ValueWithLabel>
          </SpaceBetween>

          <SpaceBetween size={SIZE}>
            {chatSystemPrompt ? (
              <ValueWithLabel label="CHAT System Prompt">
                <ExpandableSection defaultExpanded headerText="view details">
                  {chatSystemPrompt}
                </ExpandableSection>
              </ValueWithLabel>
            ) : null}
            <ValueWithLabel label="RAG System Prompt">
              <ExpandableSection defaultExpanded headerText="view details">
                {prompt}
              </ExpandableSection>
            </ValueWithLabel>
          </SpaceBetween>

          <SpaceBetween size="xs">
            {!isKendra && (
              <>
                <ValueWithLabel label="Number of doc for vector search">
                  {topK}
                </ValueWithLabel>
                <ValueWithLabel label="Number of doc for text search">
                  {txtDocsNum}
                </ValueWithLabel>
                <ValueWithLabel label="Threshold for vector search">
                  {vecDocsScoreThresholds}
                </ValueWithLabel>
                <ValueWithLabel label="Threshold for text search">
                  {txtDocsScoreThresholds}
                </ValueWithLabel>
              </>
            )}
            <Divider />
            <BoolState bool={isCheckedKnowledgeBase} text="Knowledge Base" />
            {!isKendra && (
              <>
                <BoolState
                  bool={isCheckedScoreQA}
                  text="Score Question-Answer"
                />
                <BoolState bool={isCheckedScoreQD} text="Score Question-Doc" />
                <BoolState bool={isCheckedScoreAD} text="Score Answer-Doc" />
              </>
            )}
            <BoolState bool={!!tokenContentCheck} text="Content Check" />
          </SpaceBetween>
        </Grid>
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
