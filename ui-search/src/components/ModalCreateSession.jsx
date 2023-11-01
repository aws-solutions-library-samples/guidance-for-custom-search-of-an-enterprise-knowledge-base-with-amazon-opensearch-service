import {
  Box,
  Checkbox,
  ColumnLayout,
  ExpandableSection,
  Form,
  FormField,
  Input,
  Select,
  Textarea,
  Tiles,
  Toggle,
} from '@cloudscape-design/components';
import Button from '@cloudscape-design/components/button';
import Modal from '@cloudscape-design/components/modal';
import SpaceBetween from '@cloudscape-design/components/space-between';
import { useCallback, useEffect, useState } from 'react';
import useIndexNameList from 'src/hooks/useIndexNameList';
import useInput from 'src/hooks/useInput';
import useLsLanguageModelList from 'src/hooks/useLsLanguageModelList';
import useToggle from 'src/hooks/useToggle';
import { useSessionStore } from 'src/stores/session';
import Divider from './Divider';
import useLsSessionList from 'src/hooks/useLsSessionList';

const SIZE = 's';
const OPTIONS_LANGUAGE = [
  { label: '简体中文', value: 'chinese' },
  { label: '繁体中文', value: 'chinese-tc' },
  { label: 'English', value: 'english' },
];
export const OPTIONS_SEARCH_ENGINE = [
  {
    value: 'opensearch',
    label: 'Open Search',
    description: 'A brief description of Open Search',
  },
  {
    value: 'kendra',
    label: 'Kendra',
    description: 'A brief description of Kendra',
  },
];
const OPTIONS_TOP_K = [1, 2, 3, 4].map((value) => ({
  label: `Top ${value}`,
  value,
}));

export default function ModalCreateSession({ dismissModal, modalVisible }) {
  const { addSession } = useSessionStore();
  const { lsLanguageModelList } = useLsLanguageModelList();
  const { lsSessionList, lsGetSessionItem } = useLsSessionList();
  const [name, bindName, resetName, setName] = useInput('');
  const [sessionTemplateOpt, setSessionTemplateOpt] = useState();

  const [searchEngine, bindSearchEngine, resetSearchEngine, setSearchEngine] =
    useInput(OPTIONS_SEARCH_ENGINE[0].value);
  const [llmData, setLLMData] = useState(lsLanguageModelList[0]);
  const [role, bindRole, resetRole, setRole] = useInput();

  const [language, setLanguage] = useState(OPTIONS_LANGUAGE[0].value);

  const [
    taskDefinition,
    bindTaskDefinition,
    resetTaskDefinition,
    setTaskDefinition,
  ] = useInput();
  const [outputFormat, bindOutputFormat, resetOutputFormat, setOutputFormat] =
    useInput();

  const [
    isCheckedGenerateReport,
    bindGenerateReport,
    resetGenerateReport,
    setIsCheckedGenerateReport,
  ] = useToggle(false, (checked) => {
    if (checked) {
      setIsCheckedContext(false);
      setIsCheckedKnowledgeBase(true);
    }
  });
  const [isCheckedContext, bindContext, resetContext, setIsCheckedContext] =
    useToggle(false);
  const [
    isCheckedKnowledgeBase,
    bindKnowledgeBase,
    resetKnowledgeBase,
    setIsCheckedKnowledgeBase,
  ] = useToggle(false);

  const [
    isCheckedMapReduce,
    bindMapReduce,
    resetMapReduce,
    setIsCheckedMapReduce,
  ] = useToggle(false);

  const [indexName, setIndexName] = useState('');
  const { indexNameList, loading: loadingIndexNameList } = useIndexNameList();
  const [topK, setTopK] = useState(OPTIONS_TOP_K[2].value);

  const [isCheckedScoreQA, bindScoreQA, resetScoreQA, setIsCheckedScoreQA] =
    useToggle(true);
  const [isCheckedScoreQD, bindScoreQD, resetScoreQD, setIsCheckedScoreQD] =
    useToggle(true);
  const [isCheckedScoreAD, bindScoreAD, resetScoreAD, setIsCheckedScoreAd] =
    useToggle(true);

  const [prompt, setPrompt] = useState('');

  useEffect(() => {
    let partRole = role ? `${role}. ` : '';
    const partTask = taskDefinition ? `${taskDefinition}. ` : '';
    const partOutputFormat = outputFormat || '';
    if (role) {
      if (language === 'english') {
        partRole = `You are a ${partRole}`;
        setPrompt(
          `${partRole}${partTask}${partOutputFormat}\n\nQuestion:{question}\n=========\n{context}\n=========\nAnswer:`
        );
      } else {
        partRole = `你是一名${partRole}`;
        setPrompt(
          `${partRole}${partTask}${partOutputFormat}\n\n问题:{question}\n=========\n{context}\n=========\n答案:`
        );
      }
    }
  }, [role, taskDefinition, outputFormat, language]);

  const sessionData = {
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
    prompt,
  };
  // console.log(sessionData);

  const resetAllFields = useCallback(() => {
    resetName();
    resetSearchEngine();
    setLLMData();
    resetRole();
    resetTaskDefinition();
    resetOutputFormat();
    resetGenerateReport();
    resetContext();
    resetKnowledgeBase();
    resetMapReduce();
    setIndexName('');
    // resetIndexName();
    resetScoreQA();
    resetScoreQD();
    resetScoreAD();
    setSessionTemplateOpt(undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (sessionTemplateOpt?.value) {
      const {
        configs: {
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
          prompt,
        },
      } = lsGetSessionItem(sessionTemplateOpt.value, lsSessionList);

      // setName(name);
      setSearchEngine(searchEngine);
      setLLMData(llmData);
      setRole(role);
      setLanguage(language);
      setTaskDefinition(taskDefinition);
      setOutputFormat(outputFormat);

      setIsCheckedGenerateReport(isCheckedGenerateReport);
      setIsCheckedContext(isCheckedContext);
      setIsCheckedKnowledgeBase(isCheckedKnowledgeBase);
      setIsCheckedMapReduce(isCheckedMapReduce);

      setIndexName(indexName);
      setTopK(topK);

      setIsCheckedScoreQA(isCheckedScoreQA);
      setIsCheckedScoreQD(isCheckedScoreQD);
      setIsCheckedScoreAd(isCheckedScoreAD);
    } else {
      setSessionTemplateOpt(undefined);
    }
  }, [sessionTemplateOpt, lsSessionList]);

  const [loading, setLoading] = useState(false);
  return (
    <Modal
      header="Session Configurations"
      onDismiss={dismissModal}
      visible={modalVisible}
      size="large"
      footer={
        <Box>
          <Box float="left">
            <Button onClick={resetAllFields}>Clear Fields</Button>
          </Box>
          <Box float="right">
            <Button
              variant="primary"
              loading={loading}
              iconName="insert-row"
              onClick={async () => {
                try {
                  setLoading(true);
                  await addSession(sessionData);
                  dismissModal();
                  resetAllFields();
                } catch (error) {
                  console.error(error);
                } finally {
                  setLoading(false);
                }
              }}
            >
              Create a session
            </Button>
          </Box>
        </Box>
      }
    >
      <form onSubmit={(e) => e.preventDefault()}>
        <Form>
          <SpaceBetween size={SIZE}>
            <ColumnLayout columns={2}>
              <FormField
                label="Session Name"
                description="Define a session name for future references"
              >
                <Input {...bindName} placeholder="Data search" />
              </FormField>

              {lsSessionList.length === 0 ? null : (
                <FormField
                  label="Session Template"
                  description="Select an existing session template"
                >
                  <Select
                    selectedOption={sessionTemplateOpt}
                    onChange={({ detail }) =>
                      setSessionTemplateOpt(detail.selectedOption)
                    }
                    options={lsSessionList.map(({ text, sessionId }) => ({
                      value: sessionId,
                      label: text,
                    }))}
                  />
                </FormField>
              )}
            </ColumnLayout>

            <Divider />

            <FormField
              stretch
              label="Engine"
              description="Please select a search engine"
            >
              <Tiles {...bindSearchEngine} items={OPTIONS_SEARCH_ENGINE} />
            </FormField>

            <SpaceBetween direction="vertical" size="xl">
              <ColumnLayout columns={3}>
                <FormField label="LLM" description="Please select an LLM">
                  <Select
                    empty="Add llm if no options present"
                    selectedOption={{ label: llmData?.modelName }}
                    onChange={({ detail }) => {
                      setLLMData(detail.selectedOption.value);
                    }}
                    options={lsLanguageModelList.map((item) => ({
                      label: item.modelName,
                      value: item,
                    }))}
                  />
                </FormField>
                <FormField
                  label="Role Name"
                  description="Please determine the role"
                >
                  <Input {...bindRole} placeholder="a footwear vendor" />
                </FormField>
                <FormField label="Language" description="Select a language">
                  <Select
                    selectedOption={{ value: language }}
                    onChange={({ detail }) =>
                      setLanguage(detail.selectedOption.value)
                    }
                    options={OPTIONS_LANGUAGE}
                  />
                </FormField>
              </ColumnLayout>
              <FormField
                stretch
                label="Task Definition"
                description="Please provide your task definition"
              >
                <Textarea
                  {...bindTaskDefinition}
                  rows={5}
                  placeholder="recommend appropriate footwear to the customer"
                />
              </FormField>
              <FormField
                stretch
                label="Output Format"
                description="Please provide your output format"
              >
                <Textarea
                  {...bindOutputFormat}
                  rows={1}
                  placeholder="answer in English"
                />
              </FormField>

              <SpaceBetween direction="horizontal" size="xxl">
                <FormField constraintText="This is a constraint text">
                  <Toggle {...bindGenerateReport}>Generate Report</Toggle>
                </FormField>
                <FormField constraintText="OFF when generating report">
                  <Toggle disabled={isCheckedGenerateReport} {...bindContext}>
                    Context
                  </Toggle>
                </FormField>
                <FormField
                  constraintText="Can be enabled when generating report"
                  disa
                >
                  <Toggle
                    disabled={!isCheckedGenerateReport}
                    {...bindMapReduce}
                  >
                    Map Reduce
                  </Toggle>
                </FormField>
              </SpaceBetween>

              <SpaceBetween direction="horizontal" size="xxl">
                <FormField constraintText="ON when generating report">
                  <Toggle
                    {...bindKnowledgeBase}
                    disabled={isCheckedGenerateReport}
                  >
                    Knowledge Base
                  </Toggle>
                </FormField>
                {isCheckedKnowledgeBase ? (
                  <>
                    <FormField label="Top_K">
                      <Select
                        selectedOption={{ value: topK }}
                        onChange={({ detail }) =>
                          setTopK(detail.selectedOption.value)
                        }
                        options={OPTIONS_TOP_K}
                      />
                    </FormField>
                    <FormField label="Index Name">
                      <Select
                        empty="Upload a file if no options present"
                        onChange={({ detail }) =>
                          setIndexName(detail.selectedOption.value)
                        }
                        loadingText="loading index names"
                        statusType={
                          loadingIndexNameList ? 'loading' : 'finished'
                        }
                        selectedOption={{ value: indexName }}
                        options={indexNameList.map((name) => ({ value: name }))}
                      />
                    </FormField>
                  </>
                ) : null}
              </SpaceBetween>

              <FormField stretch label="Display Scores">
                <SpaceBetween direction="horizontal" size="xxl">
                  <Checkbox {...bindScoreQA}>Query-Answer score</Checkbox>
                  <Checkbox {...bindScoreQD}>Query-Doc scores</Checkbox>
                  <Checkbox {...bindScoreAD}>Answer-Doc scores</Checkbox>
                </SpaceBetween>
              </FormField>

              <ExpandableSection
                headerText="Prompt Summary"
                defaultExpanded
                headerDescription="Generated automatically by the values of Role Name, Task Definition and Output Format"
              >
                <Textarea value={prompt} disabled rows={6} />
              </ExpandableSection>
            </SpaceBetween>
          </SpaceBetween>
        </Form>
      </form>
    </Modal>
  );
}
