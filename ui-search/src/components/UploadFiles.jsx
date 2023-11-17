import {
  Autosuggest,
  Button,
  Container,
  FileUpload,
  Form,
  FormField,
  Header,
  SpaceBetween,
  Tiles,
} from '@cloudscape-design/components';
import { useState } from 'react';
import useIndexNameList from 'src/hooks/useIndexNameList';
import useInput from 'src/hooks/useInput';
import useLsAppConfigs from 'src/hooks/useLsAppConfigs';
import { OPTIONS_SEARCH_ENGINE } from './ModalCreateSession';
import toast from 'react-hot-toast';

const SIZE = 'l';
const UploadFiles = () => {
  const { urlApiGateway, s3FileUpload } = useLsAppConfigs();
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [indexName, setIndexName] = useState('');
  const { indexNameList, loading: loadingIndexNameList } = useIndexNameList();
  const [searchEngine, bindSearchEngine, resetSearchEngine] = useInput(
    OPTIONS_SEARCH_ENGINE[0].value
  );
  const [uploading, setUploading] = useState(false);

  // console.log({ selectedFiles });
  return (
    <Container header={<Header variant="h2">Upload a file</Header>}>
      <form>
        <Form
          variant="embedded"
          actions={
            <SpaceBetween direction="horizontal" size={SIZE}>
              <Button
                loading={uploading}
                variant="primary"
                iconName="check"
                disabled={!selectedFiles.length || !indexName}
                onClick={(e) => {
                  e.preventDefault();
                  setUploading(true);
                  console.log({ selectedFiles });

                  selectedFiles.forEach((file) => {
                    const formData = new FormData();
                    formData.append('file', file);

                    try {
                      // url example: https://ttfo6y08h2.execute-api.us-west-2.amazonaws.com/prod/file_upload/intelligent-search-data-bucket-5643200499-us-west-2/source_data/index3/blogg
                      const url = `${urlApiGateway}/file_upload/${s3FileUpload}/source_data/${indexName}/${file.name}`;
                      console.log({ url });
                      fetch(url, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'multipart/form-data' },
                        body: file,
                      })
                        .then((res) => {
                          console.info('upload response:', res);
                          if (res.ok) {
                            toast.success(
                              `File: ${file.name} uploaded successfully`
                            );
                          } else {
                            toast.error(
                              `Failed to upload file: ${file.name}...`
                            );
                            console.error(res);
                          }
                        })
                        // NOTE: for single file upload, modify this if to upload multiple files
                        .finally(() => {
                          setUploading(false);
                        });
                    } catch (error) {
                      console.error(error);
                    }
                  });
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
              label="Engine"
              description="Please select a search engine"
            >
              <Tiles
                {...bindSearchEngine}
                items={OPTIONS_SEARCH_ENGINE.map((item, i) =>
                  i === 1 ? { ...item, disabled: true } : item
                )}
              />
            </FormField>
            <FormField label="Index Name" description="Database Index">
              <Autosuggest
                enteredTextLabel={(v) => `Use: "${v}"`}
                onChange={({ detail }) => setIndexName(detail.value)}
                value={indexName}
                loadingText="loading index names"
                statusType={loadingIndexNameList ? 'loading' : 'finished'}
                options={indexNameList.map((name) => ({ value: name }))}
                placeholder="Enter value"
                empty="No matches found"
              />
            </FormField>
            <FormField
              label="Select a local file"
              description="File format: pdf, ppt, doc, docx, txt, csv"
            >
              <FileUpload
                onChange={({ detail }) => setSelectedFiles(detail.value)}
                value={selectedFiles}
                // accept=".txt,.csv,.docx,.doc,.pdf"
                i18nStrings={{
                  uploadButtonText: (e) => (e ? 'Choose files' : 'Choose file'),
                  dropzoneText: (e) =>
                    e ? 'Drop files to upload' : 'Drop file to upload',
                  removeFileAriaLabel: (e) => `Remove file ${e + 1}`,
                  limitShowFewer: 'Show fewer files',
                  limitShowMore: 'Show more files',
                  errorIconAriaLabel: 'Error',
                }}
                // multiple
                showFileLastModified
                showFileSize
                showFileThumbnail
                tokenLimit={3}
                // constraintText="File format: txt, csv"
              />
            </FormField>
          </SpaceBetween>
        </Form>
      </form>
    </Container>
  );
};

export default UploadFiles;
