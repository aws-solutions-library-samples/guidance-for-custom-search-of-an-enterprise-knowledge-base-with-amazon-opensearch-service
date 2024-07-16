import {
  Autosuggest,
  Box,
  Button,
  Container,
  Form,
  FormField,
  Grid,
  Header,
  Input,
  Slider,
  SpaceBetween,
  Table,
  Tiles,
  Toggle,
} from '@cloudscape-design/components';
import React, { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import useEndpointList from 'src/hooks/useEndpointList';
import useInput from 'src/hooks/useInput';
import useLsLanguageModelList from 'src/hooks/useLsLanguageModelList';
import useToggle from 'src/hooks/useToggle';
import { LLM_DATA_TYPE } from 'src/types';
import { DEMO_SESSION_1 } from 'src/utils/PROMPT_TEMPLATES';
import { genRandomNum } from 'src/utils/genUID';

const SIZE = 'l';

export type ISagemakerModelTypeValues =
  (typeof SAGEMAKER_MODEL_TYPE)[number]['value'];
const SAGEMAKER_MODEL_TYPE = [
  { label: 'non-llama2', value: 'non_llama2' },
  { label: 'llama2', value: 'llama2' },
] as const;

export type IThirdPartyApiModelTypeValues =
  (typeof THIRD_PARTY_API_MODEL_TYPES)[number]['value'];
const THIRD_PARTY_API_MODEL_TYPES = [
  { label: 'Bedrock', value: 'bedrock' },
  { label: 'Bedrock API', value: 'bedrock_api' },
  { label: 'LLM API', value: 'llm_api' },
] as const;

export type IThirdPartyApiModelNameValues =
  (typeof THIRD_PARTY_API_MODEL_NAMES)[number]['value'];
const THIRD_PARTY_API_MODEL_NAMES = [
  { label: 'Baichuan2-53B', value: 'Baichuan2-53B', modelType: ['llm_api'] },
  { label: 'Baichuan2-192k', value: 'Baichuan2-192k', modelType: ['llm_api'] },
  {
    label: 'anthropic.claude-v2',
    value: 'anthropic.claude-v2',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-v2:1',
    value: 'anthropic.claude-v2:1',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-v1',
    value: 'anthropic.claude-v1',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-instant-v1',
    value: 'anthropic.claude-instant-v1',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'meta.llama2-13b-chat-v1',
    value: 'meta.llama2-13b-chat-v1',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-3-opus',
    value: 'anthropic.claude-3-opus-20240229-v1:0',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-3-sonnet',
    value: 'anthropic.claude-3-sonnet-20240229-v1:0',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-3-haiku',
    value: 'anthropic.claude-3-haiku-20240307-v1:0',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'anthropic.claude-3.5-sonnet',
    value: 'anthropic.claude-3-5-sonnet-20240620-v1:0',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'mistral.mistral-7b',
    value: 'mistral.mistral-7b-instruct-v0:2',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'mistral.mixtral-8x7b',
    value: 'mistral.mixtral-8x7b-instruct-v0:1',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'cohere.Command R+',
    value: 'cohere.command-r-plus-v1:0',
    modelType: ['bedrock', 'bedrock_api'],
  },
  {
    label: 'cohere.Command R',
    value: 'cohere.command-r-v1:0',
    modelType: ['bedrock', 'bedrock_api'],
  },
] as const;

const LanguageModelStrategy: React.FC = () => {
  const [strategyName, bindStrategyName, resetStrategyName] = useInput('');
  const [type, setType] = useState<LLM_DATA_TYPE>(LLM_DATA_TYPE.sagemaker);
  const [
    OptionsSagemakerEndpoint,
    OptionsEmbeddingEndpoint,
    loadingEndpointList,
  ] = useEndpointList();
  const [sagemakerEndpoint, bindSagemakerEndpoint, resetSagemakerEndpoint] =
    useInput('');
  const [temperature, setTemperature] = useState(100);
  const [maxTokens, setMaxTokens] = useState(2000);

  const [
    isSagemakerStreaming,
    bindIsSagemakerStreaming,
    resetIsSagemakerStreaming,
  ] = useToggle(true);
  const [embeddingEndpoint, bindEmbeddingEndpoint, resetEmbeddingEndpoint] =
    useInput('');
  const [
    thirdPartyEmbeddingEndpoint,
    bindThirdPartyEmbeddingEndpoint,
    resetThirdPartyEmbeddingEmbeddingEndpoint,
  ] = useInput('');
  const [thirdPartyModelType, setThirdPartyModelType] =
    useState<IThirdPartyApiModelTypeValues>(
      THIRD_PARTY_API_MODEL_TYPES[0].value
    );
  const [sagemakerModelType, setSagemakerModelType] =
    useState<ISagemakerModelTypeValues>(SAGEMAKER_MODEL_TYPE[0].value);
  const [thirdPartyModelNameOpts, setThirdPartyModelNameOpts] = useState<
    Partial<typeof THIRD_PARTY_API_MODEL_NAMES>
  >(THIRD_PARTY_API_MODEL_NAMES);
  const [thirdPartyModelName, setThirdPartyModelName] = useState<string>(
    THIRD_PARTY_API_MODEL_NAMES[0].value
  );

  const [thirdPartyApiUrl, bindThirdPartyApiUrl, resetThirdPartyApiUrl] =
    useInput('');
  const [thirdPartyApiKey, bindThirdPartyApiKey, resetThirdPartyApiKey] =
    useInput('');
  const [
    thirdPartySecretKey,
    bindThirdPartySecretKey,
    resetThirdPartySecretKey,
  ] = useInput('');

  const [validating, setValidating] = useState(false);

  useEffect(() => {
    const filteredModalNameOpts = THIRD_PARTY_API_MODEL_NAMES.filter((item) =>
      item.modelType.includes(thirdPartyModelType as never)
    ) as unknown as Partial<typeof THIRD_PARTY_API_MODEL_NAMES>;
    setThirdPartyModelName(filteredModalNameOpts[0].value);
    setThirdPartyModelNameOpts(filteredModalNameOpts);
    resetThirdPartyApiUrl();
    resetThirdPartyApiKey();
    resetThirdPartySecretKey();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [thirdPartyModelType]);

  const [isCheckedLlama2Switch, bindLlama2Switch, resetLlama2Switch] =
    useToggle(false);

  useEffect(() => {
    if (isCheckedLlama2Switch) {
      setSagemakerModelType('llama2');
    } else {
      setSagemakerModelType('non_llama2');
    }
  }, [isCheckedLlama2Switch]);

  const resetForm = useCallback(() => {
    resetStrategyName();
    resetSagemakerEndpoint();
    setTemperature(100);
    setMaxTokens(2000);
    resetIsSagemakerStreaming();
    resetEmbeddingEndpoint();
    resetThirdPartyEmbeddingEmbeddingEndpoint();
    setThirdPartyModelType(THIRD_PARTY_API_MODEL_TYPES[0].value);
    resetLlama2Switch();
    setSagemakerModelType(SAGEMAKER_MODEL_TYPE[0].value);
    resetThirdPartyApiUrl();
    resetThirdPartyApiKey();
    resetThirdPartySecretKey();
    setValidating(false);
  }, []);

  const {
    lsLanguageModelList,
    lsAddLanguageModelItem,
    lsClearLanguageModelList,
    lsDelLanguageModelItem,
  } = useLsLanguageModelList();

  return (
    <SpaceBetween size={SIZE}>
      <SpaceBetween size="s">
        <Container
          header={<Header variant="h2">Language Model Strategies</Header>}
        >
          <SpaceBetween size={SIZE}>
            <Table
              items={lsLanguageModelList}
              variant="borderless"
              empty={
                <Box
                  margin={{ vertical: 'xs' }}
                  textAlign="center"
                  color="inherit"
                >
                  <SpaceBetween size="m">
                    <b>No resources</b>
                  </SpaceBetween>
                </Box>
              }
              columnDefinitions={[
                {
                  id: 'strategyName',
                  header: 'Strategy Name',
                  width: 90,
                  cell: (item) => item.strategyName,
                },
                {
                  id: 'modelName',
                  header: 'Model Name',
                  isRowHeader: true,
                  width: 150,
                  cell: (item) => item.modelName || 'n/a',
                },
                {
                  id: 'type',
                  header: 'Type',
                  width: 120,
                  cell: (item) => item.type,
                },
                {
                  id: 'temperature',
                  header: 'Temperature',
                  width: 120,
                  cell: (item) => item.temperature || 'n/a',
                },
                {
                  id: 'maxTokens',
                  header: 'Max Tokens',
                  width: 120,
                  cell: (item) => item.maxTokens || 'n/a',
                },
                {
                  id: 'modelType',
                  header: 'Model Type',
                  width: 50,
                  cell: (item) => item.modelType,
                },
                {
                  id: 'sagemakerEndpoint',
                  header: 'SageMaker Endpoint',
                  width: 200,
                  cell: (item) => item.sagemakerEndpoint || 'n/a',
                },
                {
                  id: 'embeddingEndpoint',
                  header: 'EmbeddingEndpoint',
                  width: 200,
                  cell: (item) => {
                    if (item.isCheckedTitanEmbedding)
                      return 'Use Titan Embedding';
                    return item.embeddingEndpoint || 'n/a';
                  },
                },
                {
                  id: 'apiUrl',
                  header: 'API URL',
                  width: 200,
                  cell: (item) => item.apiUrl || 'n/a',
                },
                {
                  id: 'apiKey',
                  header: 'API Key',
                  width: 200,
                  cell: (item) => item.apiKey || 'n/a',
                },
                {
                  id: 'secretKey',
                  header: 'Secret Key',
                  width: 200,
                  cell: (item) => item.secretKey || 'n/a',
                },
                {
                  id: 'operations',
                  header: 'Operations',
                  width: 20,
                  cell: (item) => (
                    <SpaceBetween size="xxs">
                      <Button
                        iconName="remove"
                        onClick={() => {
                          const bool = window?.confirm(
                            'Confirm to delete this language model strategy?'
                          );
                          if (bool) lsDelLanguageModelItem(item.recordId);
                        }}
                        disabled={[
                          DEMO_SESSION_1.configs.llmData.recordId,
                        ].includes(item.recordId)}
                      />
                    </SpaceBetween>
                  ),
                },
              ]}
            />
            <Box float="right">
              <Button
                onClick={() => {
                  const bool = window?.confirm('Confirm to clear this list?');
                  if (bool) lsClearLanguageModelList();
                }}
              >
                Delete all language model strategies
              </Button>
            </Box>
          </SpaceBetween>
        </Container>
      </SpaceBetween>

      <Container
        header={<Header variant="h2">Create a language model strategy</Header>}
      >
        <form onSubmit={(e) => e.preventDefault()}>
          <Form
            variant="embedded"
            actions={
              <SpaceBetween alignItems="center" size={SIZE}>
                <Button
                  variant="primary"
                  iconName="status-positive"
                  onClick={() => {
                    setValidating(true);
                    if (!strategyName)
                      return toast.error('Please provide Strategy Name');

                    try {
                      let values;
                      if (type === LLM_DATA_TYPE.sagemaker) {
                        // SageMaker endpoint
                        values = {
                          strategyName,
                          type,
                          embeddingEndpoint,
                          modelType: sagemakerModelType,
                          recordId: `${sagemakerEndpoint}-${genRandomNum()}`,
                          temperature: temperature / 100,
                          maxTokens,
                          // *** different items
                          sagemakerEndpoint,
                          streaming: isSagemakerStreaming,
                        };
                      } else {
                        // Third Party APIs
                        values = {
                          strategyName,
                          type,
                          embeddingEndpoint: thirdPartyEmbeddingEndpoint,
                          modelType: thirdPartyModelType,
                          modelName: thirdPartyModelName,
                          recordId: `${thirdPartyModelName}-${genRandomNum()}`,
                          temperature: temperature / 100,
                          maxTokens,
                          // *** different items
                          apiUrl: thirdPartyApiUrl,
                          apiKey: thirdPartyApiKey,
                          secretKey: thirdPartySecretKey,
                        };
                      }
                      lsAddLanguageModelItem(values);
                      resetForm();
                    } catch (error) {
                      console.error(error);
                    } finally {
                      setValidating(false);
                    }
                  }}
                >
                  Confirm
                </Button>
              </SpaceBetween>
            }
          >
            <SpaceBetween size={SIZE}>
              <FormField
                stretch
                label="Strategy Name"
                errorText={
                  validating && !strategyName && 'Please provide Strategy Name'
                }
              >
                <Input
                  {...bindStrategyName}
                  placeholder="Please provide a name for this language model strategy"
                />
              </FormField>
              <FormField stretch label="Please select the endpoint type">
                <Tiles
                  value={type}
                  onChange={(e) => setType(e.detail.value as LLM_DATA_TYPE)}
                  items={[
                    {
                      value: LLM_DATA_TYPE.sagemaker,
                      label: 'SageMaker Endpoint',
                      description:
                        'Deployed service for real-time ML model inference',
                    },
                    {
                      value: LLM_DATA_TYPE.thirdParty,
                      label: 'Third Party APIs',
                      description: 'Options are Bedrock, Claude, ChatGLM etc.',
                    },
                  ]}
                />
              </FormField>

              <Grid gridDefinition={[{ colspan: 6 }, { colspan: 6 }]}>
                <FormField stretch label="Temperature">
                  <Grid
                    gridDefinition={[
                      { colspan: { default: 6, xxs: 9 } },
                      { colspan: { default: 6, xxs: 3 } },
                    ]}
                  >
                    <Slider
                      value={temperature}
                      onChange={({ detail }) => setTemperature(detail.value)}
                      max={100}
                      min={0}
                      // referenceValues={[50]}
                      valueFormatter={(value) => (value / 100).toString()}
                    />
                    <Input
                      type="number"
                      inputMode="numeric"
                      value={(temperature / 100).toString()}
                      step={0.01}
                      onChange={({ detail }) => {
                        setTemperature(() => {
                          const n = Number(detail.value) * 100;
                          if (n > 100) return 100;
                          if (n < 0) return 0;
                          return n;
                        });
                      }}
                    />
                  </Grid>
                </FormField>
                <FormField stretch label="Max Tokens">
                  <Grid
                    gridDefinition={[
                      { colspan: { default: 6, xxs: 9 } },
                      { colspan: { default: 6, xxs: 3 } },
                    ]}
                  >
                    <Slider
                      value={maxTokens}
                      onChange={({ detail }) => setMaxTokens(detail.value)}
                      max={8192}
                      min={0}
                      // referenceValues={[4096]}
                      valueFormatter={(value) => value.toString()}
                    />
                    <Input
                      type="number"
                      inputMode="numeric"
                      value={maxTokens.toString()}
                      step={1}
                      onChange={({ detail }) => {
                        setMaxTokens(() => {
                          const n = Number(detail.value);
                          if (n > 8192) return 8192;
                          if (n < 0) return 0;
                          return n;
                        });
                      }}
                    />
                  </Grid>
                </FormField>
              </Grid>

              {type === LLM_DATA_TYPE.sagemaker ? (
                // **** SageMaker *************************************************************
                <>
                  <Grid gridDefinition={[{ colspan: 6 }, { colspan: 6 }]}>
                    <FormField>
                      <Toggle {...bindIsSagemakerStreaming}>
                        Streaming output
                      </Toggle>
                    </FormField>
                    <FormField>
                      <Toggle {...bindLlama2Switch}>
                        LLama2 model deployed through Jumpstart
                      </Toggle>
                    </FormField>
                  </Grid>

                  <FormField label="SageMaker Endpoint">
                    <Autosuggest
                      enteredTextLabel={(v) => `Use: "${v}"`}
                      {...bindSagemakerEndpoint}
                      loadingText="loading endpoint list"
                      statusType={loadingEndpointList ? 'loading' : 'finished'}
                      options={OptionsSagemakerEndpoint}
                      placeholder="Search or enter value"
                      empty="No matches found"
                    />
                  </FormField>

                  <FormField label="Embedding Endpoint">
                    <Autosuggest
                      enteredTextLabel={(v) => `Use: "${v}"`}
                      {...bindEmbeddingEndpoint}
                      loadingText="loading endpoint list"
                      statusType={loadingEndpointList ? 'loading' : 'finished'}
                      options={OptionsEmbeddingEndpoint}
                      placeholder="Search or enter value"
                      empty="No matches found"
                    />
                  </FormField>
                </>
              ) : (
                // **** Third Party ***********************************************************
                <>
                  <FormField label="Model Type" stretch>
                    <Tiles
                      columns={4}
                      onChange={({ detail }) =>
                        setThirdPartyModelType(
                          detail.value as IThirdPartyApiModelTypeValues
                        )
                      }
                      value={thirdPartyModelType}
                      items={THIRD_PARTY_API_MODEL_TYPES}
                    />
                  </FormField>
                  <FormField label="Model Name" stretch>
                    <Tiles
                      columns={4}
                      onChange={({ detail }) =>
                        setThirdPartyModelName(detail.value)
                      }
                      value={thirdPartyModelName}
                      items={thirdPartyModelNameOpts}
                    />
                  </FormField>

                  <FormField label="Embedding Endpoint">
                    <Autosuggest
                      enteredTextLabel={(v) => `Use: "${v}"`}
                      {...bindThirdPartyEmbeddingEndpoint}
                      loadingText="loading endpoint list"
                      statusType={loadingEndpointList ? 'loading' : 'finished'}
                      options={OptionsEmbeddingEndpoint}
                      placeholder="Search or enter value"
                      empty="No matches found"
                    />
                  </FormField>
                  {thirdPartyModelType ===
                  'bedrock' ? null : thirdPartyModelType === 'bedrock_api' ? (
                    <>
                      <FormField label="API URL">
                        <Input
                          {...bindThirdPartyApiUrl}
                          placeholder="Please provide API URL"
                        />
                      </FormField>
                    </>
                  ) : thirdPartyModelType === 'llm_api' ? (
                    <>
                      <FormField label="API URL">
                        <Input
                          {...bindThirdPartyApiUrl}
                          placeholder="Please provide API URL"
                        />
                      </FormField>
                      <FormField label="API Key">
                        <Input
                          {...bindThirdPartyApiKey}
                          placeholder="Please provide API Key"
                        />
                      </FormField>
                      <FormField label="Secret Key">
                        <Input
                          {...bindThirdPartySecretKey}
                          placeholder="Please provide Secret Key"
                        />
                      </FormField>
                    </>
                  ) : null}
                </>
              )}
            </SpaceBetween>
          </Form>
        </form>
      </Container>
    </SpaceBetween>
  );
};

export default LanguageModelStrategy;
