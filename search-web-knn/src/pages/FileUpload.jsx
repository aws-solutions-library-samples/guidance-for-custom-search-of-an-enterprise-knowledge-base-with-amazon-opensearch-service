import React, {useState, useEffect} from 'react';
import Alert from "@cloudscape-design/components/alert";
import {
    Button,
    RadioGroup,
    SpaceBetween,
    FormField, Grid,
} from '@cloudscape-design/components';
import {CustomAppLayout, TableNoMatchState, TableHeader} from './common/common-components';
import {MyNavigation} from './common/mynavigation';

import axios from 'axios'
import FileUpload from "@cloudscape-design/components/file-upload";

import {
    mainapi,
    FILE_TYPES,
    SOURCE_DATA_BUCKET,
    SOURCE_DATA_BUCKET_PREFIX
} from '../pages/common/constants'

function App({distributions}) {

    const [uploadedFileName, setUploadedFileName] = useState('')
    const [upload_status, setUploadSuccess] = useState('')
    const [file_selected, setSelectedFileName] = useState([])
    const [file_type, setFileType] = React.useState("faq");

    const upload_file = (e, files) => {

        files.forEach((file) => {

            const fileObj = file
            const _request_url = mainapi + '/file_upload/' + SOURCE_DATA_BUCKET + "/" + SOURCE_DATA_BUCKET_PREFIX + file_type + "/" + file['name']
            console.log(_request_url)

            // Don't use FormData, because it will serialized the data and upload to S3, which led to file corrupted.
            return axios.put(_request_url, fileObj, {
                headers: {
                    "Content-Type": "multipart/form-data"
                },
            }).then((response) => {
                console.info("upload response:", response)
                setUploadedFileName(file['name'])

                let statusCode = response['status']
                if (statusCode == 200) {
                    // pop notification Success
                    console.log("Upload successfully")
                    setUploadSuccess(true)
                } else {
                    // pop notification Fail, with ERROR
                    console.log("Upload failed")
                    console.log(response)
                }

            })
        })
    }

    const FileTypeRadioGroup = () => {

        return (
            <RadioGroup
                onChange={({detail}) => setFileType(detail.value)}
                value={file_type}
                items={FILE_TYPES}
            />
        );
    }

    const FileUploadPanel = () => {

        return (
            <SpaceBetween size="s" direction="horizontal">
                <FormField
                    label="Data Preparation for Financial"
                    description="Please upload single or multiple files"
                >
                    <FileUpload
                        onChange={({detail}) => setSelectedFileName(detail.value)}
                        value={file_selected}
                        i18nStrings={{
                            uploadButtonText: e =>
                                e ? "Choose files" : "Choose file",
                            dropzoneText: e =>
                                e
                                    ? "Drop files to upload"
                                    : "Drop file to upload",
                            removeFileAriaLabel: e =>
                                `Remove file ${e + 1}`,
                            limitShowFewer: "Show fewer files",
                            limitShowMore: "Show more files",
                            errorIconAriaLabel: "Error"
                        }}
                        ariaRequired={true}
                        multiple
                        showFileLastModified
                        showFileSize
                        showFileThumbnail
                        tokenLimit={3}
                        constraintText="Word/PDF supported, with single file size less than 5MB."
                    />
                    <br/>
                    <FileTypeRadioGroup/>
                    <br/>
                    <Button variant="primary"
                            onClick={(e) => upload_file(e, file_selected)}>{'Upload File(s)'}</Button>
                </FormField>

            </SpaceBetween>
        )
    }

    function Notifications() {
//    Display notification when file uploaded, or failed
        return (
            <React.Fragment>
                {upload_status == '' ? null :
                    upload_status ? (
                        <Alert dismissible
                               type="success"
                               statusIconAriaLabel="Success">
                            File [ {uploadedFileName} ] uploaded !
                        </Alert>) : (
                        <Alert dismissible
                               type="error"
                               statusIconAriaLabel="Success">
                            Unable to upload file [{uploadedFileName}].
                        </Alert>)}
            </React.Fragment>
        );
    }

    function FileUploadSegment(distributions) {
        return (
            <>
                <Grid
                    gridDefinition={[
                        {colspan: {l: 12, m: 12, default: 12}},
                        {colspan: {l: 12, m: 12, default: 12}},
                        {colspan: {l: 12, m: 12, default: 12}},
                    ]}
                >
                    <Button variant="link" disabled>{''}</Button>
                    <Notifications/>
                    <FileUploadPanel/>
                </Grid>
            </>
        )
    }


    return (
        <CustomAppLayout
            navigation={<MyNavigation/>}
            content={<FileUploadSegment distributions={distributions}/>}
            contentType="table"
            stickyNotifications
        />
    );
}

function SearchMain() {
    return (
        <App/>
    );
}

export default SearchMain;
