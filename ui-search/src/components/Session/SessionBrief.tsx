import {
  Box,
  Button,
  Container,
  ExpandableSection,
  Grid,
  Header,
  Popover,
  SpaceBetween,
  StatusIndicator,
} from '@cloudscape-design/components';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DEFAULT_WORK_MODE } from 'src/constants';
import { getSystemPrompt } from 'src/hooks/useApiOrchestration';
import { useSessionStore } from 'src/stores/session';
import { WORK_MODE, WORK_MODULE } from 'src/types';
import Divider from '../Divider';
import StateLoading from '../StateLoading';
import ValueWithLabel from '../ValueWithLabel';

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
    isCheckedTextRAGOnlyOnMultiModal,
    workFlowLocal,
    language,
    contextRounds,
    isCheckedKnowledgeBase,
    indexName,
    vecTopK,
    searchMethod,
    txtTopK,
    vecDocsScoreThresholds,
    txtDocsScoreThresholds,
    isCheckedScoreQA,
    isCheckedScoreQD,
    isCheckedScoreAD,
    sessionId,
  } = configs;

  const chatSystemPrompt = getSystemPrompt(WORK_MODULE.CHAT, workFlowLocal);
  const ragSystemPrompt = getSystemPrompt(WORK_MODULE.RAG, workFlowLocal);

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

            <ValueWithLabel label="Index Name">{indexName}</ValueWithLabel>
            <ValueWithLabel label="Search Method">
              {searchMethod}
            </ValueWithLabel>
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
                {ragSystemPrompt}
              </ExpandableSection>
            </ValueWithLabel>
          </SpaceBetween>

          <SpaceBetween size="xs">
            <ValueWithLabel label="Number of doc for vector search">
              {vecTopK}
            </ValueWithLabel>
            <ValueWithLabel label="Number of doc for text search">
              {txtTopK}
            </ValueWithLabel>
            <ValueWithLabel label="Threshold for vector search">
              {vecDocsScoreThresholds}
            </ValueWithLabel>
            <ValueWithLabel label="Threshold for text search">
              {txtDocsScoreThresholds}
            </ValueWithLabel>
            <Divider />
            {workMode === WORK_MODE.multiModal && (
              <BoolState
                bool={isCheckedTextRAGOnlyOnMultiModal}
                text="Bypass CHAT"
              />
            )}
            <BoolState bool={isCheckedKnowledgeBase} text="Knowledge Base" />
            <BoolState bool={isCheckedScoreQA} text="Score Question-Answer" />
            <BoolState bool={isCheckedScoreQD} text="Score Question-Doc" />
            <BoolState bool={isCheckedScoreAD} text="Score Answer-Doc" />
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
