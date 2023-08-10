// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import React from 'react';
import { CollectionPreferences} from '@cloudscape-design/components';


// const api = 'https://w0bjmbcfil.execute-api.us-east-2.amazonaws.com/opensearch-api-test'
// const HEADERS = {'Content-Type': 'application/json'}

// const insertFeedback = (
//   search_inputs,
//   _id,
//   datetime,
//   feedback,
// ) => {
//   pyload = {
//       "Method": "insert_feedback",
//       "table_name": "FeedbackRecords",
//       "datetime": datetime,
//       "search_inputs": search_inputs,
//       "_id": _id,
//       "feedback": feedback
//     }
//   axios({ method: 'POST', url: apiurl, data: pyload, headers: HEADERS}).then(response => {
//     console.log(response);
//     })
// }

// function ResponseIcon({ _item }){
//   const [upVariant, setUpVariant] = useState("icon" );
//   const [downVariant, setDownVariant] = useState("icon");
//   const [upStyle, setUpStyle] = useState("caret-up-filled" );
//   const [downStyle, setDownStyle] = useState("caret-down-filled");

//   const upDataIncon = (e,
//     up=false,
//    ) => {
//     if (up){
//       setUpVariant("primary")
//       setDownVariant("icon")
//       console.log('*********##########x')
//       console.log(_item)
//       // {(e)=>insertFeedback(e, true)}
//     }
//     else{
//       setUpVariant("icon")
//       setDownVariant("primary")
//     }
//     return up;
//   }
//   // onsole.log({item})
//   return (
//   <div>
//     {/* <Button variant="link" onClick={upDataIncon}>{'↑'}</Button>
//     <Button variant="link" onClick={upDataIncon}>{'↓'}</Button> */}
//     {/* <Button
//       iconName="caret-up-filled"
//       variant="primary"
//     /> */}
//     <Button iconName={upStyle} variant={upVariant} onClick={(e)=>upDataIncon(e, true)}/>
//     <Button iconName={downStyle} variant={downVariant} onClick={(e)=>upDataIncon(e, false)}/>
//   </div>
//   );
// }

// export const COLUMN_DEFINITIONS = addColumnSortLabels([
//   {
//     id: '_id',
//     sortingField: '_id',
//     // header: 'Distribution ID',
//     header: 'ID',
//     cell: item => item._id,
//     minWidth: 100,
//   },
//   {
//     id: '_feedback',
//     sortingField: '_feedback',
//     // header: 'Distribution ID',
//     header: 'Feedback',
//     // cell: item => item._id,
//     cell: item => (
//       <div>
//         <ResponseIcon _item={item}/>
//       </div>
//     ),
//     minWidth: 100,
//   },
//   {
//     id: '_score',
//     sortingField: '_score',
//     header: 'Score',
//     cell: item => (
//       <StatusIndicator type={item.state === 'Deactivated' ? 'error' : 'success'}>{item._score}</StatusIndicator>
//     ),
//     minWidth: 120,
//   },
//   {
//     id: 'description',
//     sortingField: 'description',
//     cell: item => item.description,
//     header: 'Description',
//     minWidth: 160,
//   },
//   {
//     id: 'detection',
//     sortingField: 'detection',
//     header: 'Detection',
//     cell: item => item.detection,
//     minWidth: 100,
//   },
//   // {
//   //   id: 'priceClass',
//   //   sortingField: 'priceClass',
//   //   header: 'Price class',
//   //   cell: item => item.priceClass,
//   //   minWidth: 100,
//   // },
//   // {
//   //   id: 'sslCertificate',
//   //   sortingField: 'sslCertificate',
//   //   header: 'SSL certificate',
//   //   cell: item => item.sslCertificate,
//   //   minWidth: 100,
//   // },
//   // {
//   //   id: 'origin',
//   //   sortingField: 'origin',
//   //   header: 'Origin',
//   //   cell: item => item.origin,
//   //   minWidth: 100,
//   // },
//   // {
//   //   id: 'status',
//   //   sortingField: 'status',
//   //   header: 'Status',
//   //   cell: item => item.status,
//   //   minWidth: 100,
//   // },
//   // {
//   //   id: 'logging',
//   //   sortingField: 'logging',
//   //   header: 'Logging',
//   //   cell: item => item.logging,
//   //   minWidth: 100,
//   // },
// ]);

const VISIBLE_CONTENT_OPTIONS = [
  {
    label: 'Main distribution properties',
    options: [
      { id: '_feedback', label: 'Feedback' },
      { id: '_id', label: 'ID' },
      { id: 'description', label: 'description' },
      { id: 'detection', label: 'Detection' },
      // { id: 'priceClass', label: 'Price class' },
      // { id: 'sslCertificate', label: 'SSL certificate' },
      // { id: 'origin', label: 'Origin' },
      // { id: 'status', label: 'Status' },
      { id: '_score', label: 'Score' },
      // { id: 'logging', label: 'Logging' },
    ],
  },
];

export const PAGE_SIZE_OPTIONS = [
  { value: 10, label: '10 Distributions' },
  { value: 30, label: '30 Distributions' },
  { value: 50, label: '50 Distributions' },
];

export const DEFAULT_PREFERENCES = {
  pageSize: 30,
  visibleContent: ['_feedback', '_score', 'description', 'detection'],
  wrapLines: false,
};

export const Preferences = ({
  preferences,
  setPreferences,
  disabled,
  pageSizeOptions = PAGE_SIZE_OPTIONS,
  visibleContentOptions = VISIBLE_CONTENT_OPTIONS,
}) => (
  <CollectionPreferences
    title="Preferences"
    confirmLabel="Confirm"
    cancelLabel="Cancel"
    disabled={disabled}
    preferences={preferences}
    onConfirm={({ detail }) => setPreferences(detail)}
    pageSizePreference={{
      title: 'Page size',
      options: pageSizeOptions,
    }}
    wrapLinesPreference={{
      label: 'Wrap lines',
      description: 'Check to see all the text and wrap the lines',
    }}
    visibleContentPreference={{
      title: 'Select visible columns',
      options: visibleContentOptions,
    }}
  />
);
