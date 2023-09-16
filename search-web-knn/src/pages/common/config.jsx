// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import React from 'react';
import { CollectionPreferences} from '@cloudscape-design/components';

export var TABLE_COL_CUSTOME = ['fid', 'fname', 'fmodel', 'fhelpcode']




var TABLE_ORI = ['_feedback', '_score']
var TABLE_COL = TABLE_ORI.concat(TABLE_COL_CUSTOME)

var VISIBLE_CONTENT_OPTIONS_VAL = [
  { id: '_feedback', label: 'Feedback' },
  { id: '_id', label: 'ID' },
  { id: '_score', label: 'Score' }]

TABLE_COL_CUSTOME.forEach((v, i)=>{
  VISIBLE_CONTENT_OPTIONS_VAL.push({id: v, label: v})
});
const VISIBLE_CONTENT_OPTIONS = [
  {
    label: 'Main distribution properties',
    options: VISIBLE_CONTENT_OPTIONS_VAL
  },
];

export const PAGE_SIZE_OPTIONS = [
  { value: 10, label: '10 Distributions' },
  { value: 30, label: '30 Distributions' },
  { value: 50, label: '50 Distributions' },
];

export const DEFAULT_PREFERENCES = {
  pageSize: 30,
  visibleContent: TABLE_COL,
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
